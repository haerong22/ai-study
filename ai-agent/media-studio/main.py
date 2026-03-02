from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from create_image_crew import CreateImageService
from edit_image_crew import EditImageService
from env import TELEGRAM_BOT_TOKEN, REPLICATE_API_TOKEN



class ImageStudioBot:
    def __init__(self, telegram_token, replicate_token):
        self.telegram_token = telegram_token
        self.replicate_token = replicate_token
        self.create_service = CreateImageService(replicate_token)
        self.edit_service = EditImageService(replicate_token)
        self.user_sessions = {}
        self.application = Application.builder().token(telegram_token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        # 명령 핸들러 등록
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))

        # 메시지 핸들러
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )
        self.application.add_handler(
            MessageHandler(filters.PHOTO, self.handle_photo_message)
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = (
            "Image Studio Bot에 오신 것을 환영합니다!\n\n"
            "이 봇으로 AI를 활용한 이미지 생성과 편집을 할 수 있습니다!\n\n"
            "주요 기능:\n\n"
            "1. 텍스트→이미지 생성\n"
            "   • 텍스트만 입력하면 새로운 이미지 생성\n"
            '   • 예: "장발의 잘생긴 30대 한국 남자 전신샷"\n\n'
            "2. 이미지 편집\n"
            "   • 이미지 + 편집설명을 함께 보내세요\n"
            '   • 예: 이미지 첨부 + "신발을 나이키 하얀색으로 바꿔줘"\n\n'
            "3. 연속 편집\n"
            "   • 이미지 생성 후 텍스트만 보내면 추가 편집\n"
            "   • 원하는 만큼 계속 수정 가능!\n\n"
            "4. 명령어:\n"
            "   • `/help` - 자세한 사용법 보기\n"
            "   • `/clear`, `q`, `end` - 작업 종료\n\n"
            "지금 바로 시작해보세요!\n"
            "텍스트를 입력하거나 이미지+설명을 보내주세요!"
        )
        if update.message:
            await update.message.reply_text(welcome_message, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = (
            "Image Studio Bot 사용 가이드\n\n"
            "1. 텍스트→이미지 생성\n"
            "   • 텍스트만 입력하세요\n"
            '   • 예시: "장발의 잘생긴 30대 한국 남자 전신샷"\n'
            "   • AI가 자동으로 최적화된 이미지 생성\n\n"
            "2. 이미지 편집 (새 이미지)\n"
            "   • 이미지 선택 → 설명란에 편집내용 입력 → 전송\n"
            '   • 예시: 사진 + "신발을 나이키 하얀색으로 바꿔줘"\n'
            "   • 기존 작업이 있으면 자동으로 새 세션 시작\n\n"
            "3. 연속 편집 (기존 이미지)\n"
            "   • 이미지 생성/편집 후 텍스트만 입력\n"
            '   • 예시: "머리색을 갈색으로 바꿔줘"\n'
            "   • 같은 이미지를 계속 수정 가능\n\n"
            "4. 세션 관리\n"
            "   • `q` 또는 `end` - 현재 작업 종료\n"
            "   • `/clear` - 세션 초기화\n"
            "   • 새 이미지 업로드 시 자동 세션 전환\n\n"
            "실전 예시:\n"
            '1. "30대 남성 정장 차림" (이미지 생성)\n'
            '2. "넥타이를 빨간색으로 바꿔줘" (연속 편집)\n'
            '3. "배경을 사무실로 바꿔줘" (연속 편집)\n'
            "4. `q` (작업 종료)\n\n"
            "팁: 구체적인 설명일수록 더 정확한 결과를 얻을 수 있어요!"
        )
        if update.message:
            await update.message.reply_text(help_message, parse_mode="Markdown")

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user and update.effective_user.id:
            await self.clear_session(update.effective_user.id)
        if update.message:
            await update.message.reply_text(
                "세션이 초기화되었습니다. 새로운 작업을 시작할 수 있습니다!"
            )

    async def handle_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """사용자가 텍스트를 보낸 경우"""
        if update.effective_user and update.effective_user.id:
            user_id = update.effective_user.id

        if not update.message:
            return

        # 사용자 메시지
        text = str(update.message.text).strip()

        # 종료 명령어 --> 세션 종료
        if text.lower() in ["q", "end"]:
            await self.clear_session(user_id)
            await update.message.reply_text(
                "세션이 종료되었습니다. 새로운 작업을 시작할 수 있습니다!"
            )
            return

        try:
            # 세션이 없을 경우 --> 새로운 세션 초기화
            if user_id not in self.user_sessions:

                self.user_sessions[user_id] = {
                    "current_image": None,
                    "generated_images": [],
                }

            session = self.user_sessions[user_id]

            # 세션에 현재 이미지가 없을 경우 --> 이미지 생성
            if session["current_image"] is None:
                await update.message.reply_text(
                    "이미지를 생성하고 있습니다... 잠시만 기다려주세요!"
                )

                image_path = self.create_service.create_image(text)
                session["current_image"] = image_path
                session["generated_images"].append(image_path)

                with open(image_path, "rb") as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"✨ 이미지가 생성되었습니다!\n프롬프트: {text}\n\n다른 텍스트를 보내서 이미지를 편집하거나 'q'를 입력해서 종료하세요.",
                    )

            # 세션에 현재 이미지가 있는 경우 --> 이미지 편집
            else:
                await update.message.reply_text(
                    "🖌️ 이미지를 편집하고 있습니다... 잠시만 기다려주세요!"
                )

                edited_image_path = self.edit_service.edit_image(
                    session["current_image"], text
                )
                session["current_image"] = edited_image_path
                session["generated_images"].append(edited_image_path)

                with open(edited_image_path, "rb") as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=f"✨ 이미지가 편집되었습니다!\n편집 내용: {text}\n\n계속 편집하거나 'q'를 입력해서 종료하세요.",
                    )

        except Exception as e:
            await update.message.reply_text(f"❌ 오류가 발생했습니다: {str(e)}")

    async def handle_photo_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """사용자가 이미지를 보낸 경우 --> 세로운 세션 시작 내포"""
        if update.effective_user is None:
            return
        if update.message is None:
            return

        user_id = update.effective_user.id
        caption = update.message.caption or ""

        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)

            if not caption.strip():
                await update.message.reply_text(
                    "이미지를 받았습니다\n\n"
                    "이미지 편집을 위해서는 편집 내용을 함께 보내주셔야 합니다.**\n\n"
                    "사용 방법:\n"
                    "1. 이미지를 선택하세요\n"
                    "2. 이미지 설명란에 편집 내용을 작성하세요\n"
                    "3. 함께 보내세요\n\n"
                    "예시:\n"
                    '• "신발을 나이키 하얀색 신발로 바꿔줘"\n'
                    '• "배경을 바다로 변경해줘"\n'
                    '• "옷을 빨간색 드레스로 바꿔줘"\n\n'
                    "다시 이미지를 편집 내용과 함께 보내주세요!",
                    parse_mode="Markdown",
                )
                return

            # 이미지 + 편집 설명이 있는 경우 --> 작업 시작! (새로운 세션 시작)

            # 기존 세션이 있다면 세션을 종료하고 새로 시작한다고 안내
            if (
                user_id in self.user_sessions
                and self.user_sessions[user_id]["current_image"]
            ):
                await update.message.reply_text(
                    "새로운 이미지 편집을 시작합니다!\n"
                    "이전 작업은 자동으로 정리됩니다."
                )

            await self.clear_session(user_id)

            # 새로운 세션 초기화
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "current_image": None,
                    "generated_images": [],
                }

            session = self.user_sessions[user_id]

            await update.message.reply_text(
                f"이미지를 편집하고 있습니다...\n"
                f"편집 내용: `{caption.strip()}`\n\n"
                f"잠시만 기다려주세요!",
                parse_mode="Markdown",
            )

            # 편집을 위해서 텔레그램에서 보낸 이미지를 저장
            input_image_path = self.edit_service.download_telegram_image(
                file.file_path, self.telegram_token
            )
            session["generated_images"].append(input_image_path)

            # 이미지 편집 진행
            edited_image_path = self.edit_service.edit_image(
                input_image_path, caption.strip()
            )

            # 편집된 이미지 세션에 저장
            session["current_image"] = edited_image_path
            session["generated_images"].append(edited_image_path)

            # 편집된 이미지 전송
            with open(edited_image_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=(
                        f"이미지가 편집되었습니다!\n"
                        f"편집 내용: {caption}\n\n"
                        f"다음 작업:\n"
                        f"• 더 편집하려면 텍스트만 보내세요\n"
                        f"• 새 이미지 편집은 이미지+설명 함께 보내세요\n"
                        f"• 작업 종료는 `q` 또는 `end` 입력\n\n"
                        f"지금 바로 추가 편집 내용을 텍스트로 보내보세요!"
                    ),
                )

        except Exception as e:
            await update.message.reply_text(f"오류가 발생했습니다: {str(e)}")

    async def clear_session(self, user_id):
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]

            if session["generated_images"]:
                self.create_service.cleanup_images(session["generated_images"])

            self.user_sessions[user_id] = {
                "current_image": None,
                "generated_images": [],
            }

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

bot = ImageStudioBot(TELEGRAM_BOT_TOKEN, REPLICATE_API_TOKEN)
bot.run()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from create_video_crew import CreateVideoService


class VideoCreatorBot:
    def __init__(self, telegram_token, replicate_token):

        self.telegram_token = telegram_token
        self.replicate_token = replicate_token
        self.create_service = CreateVideoService(replicate_token)

        # User session storage - {user_id: {"generated_videos": [paths]}}
        self.user_sessions = {}

        self.application = Application.builder().token(telegram_token).build()

        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))

        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "Video Creator Bot에 오신 것을 환영합니다!\n\n"
            "이 봇으로 AI를 활용한 동영상 생성을 할 수 있습니다!\n\n"
            "주요 기능:\n\n"
            "텍스트→동영상 생성\n"
            "   • 텍스트만 입력하면 새로운 동영상 생성\n"
            '   • 예: "바다에서 춤추는 여자"\n'
            '   • 예: "도시 야경의 자동차 불빛"\n'
            '   • 예: "숲속에서 뛰어노는 강아지"\n\n'
            "사용법:\n"
            "   • 원하는 동영상 내용을 텍스트로 설명하세요\n"
            "   • AI가 자동으로 최적화된 동영상 생성\n"
            "   • 움직임, 색감, 분위기를 구체적으로 설명할수록 좋아요!\n\n"
            "명령어:\n"
            "   • `/help` - 자세한 사용법 보기\n"
            "   • `/clear` - 세션 정리\n\n"
            "지금 바로 시작해보세요!\n"
            "원하는 동영상 내용을 텍스트로 설명해주세요!"
        )
        if not update.message:
            return
        await update.message.reply_text(welcome_message, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_message = (
            "Video Creator Bot 사용 가이드\n\n"
            "텍스트→동영상 생성\n"
            "   • 텍스트로 원하는 동영상 내용을 설명하세요\n"
            "   • AI가 ByteDance Seedance 모델로 동영상 생성\n"
            "   • 생성 시간: 약 1-3분 소요\n\n"
            "좋은 프롬프트 작성 팁\n"
            '   • 주요 객체와 행동을 명시: "춤추는 여자", "걷는 남자"\n'
            '   • 배경과 환경 설명: "바다에서", "숲속에서", "도시에서"\n'
            '   • 움직임 표현: "천천히", "빠르게", "우아하게"\n'
            '   • 분위기 설정: "로맨틱한", "신비로운", "활기찬"\n'
            '   • 조명 조건: "황금빛 석양", "밤의 네온사인", "자연광"\n\n'
            "실전 예시:\n"
            '   • "바다 위에서 우아하게 춤추는 발레리나, 석양 배경"\n'
            '   • "도시 야경에서 빠르게 지나가는 자동차들의 불빛"\n'
            '   • "숲속에서 천천히 걸어가는 사람, 아침 햇살"\n'
            '   • "카페에서 커피를 마시는 여자, 따뜻한 조명"\n\n'
            "명령어:\n"
            "   • `/clear` - 생성된 동영상 정리\n\n"
            "주의사항:\n"
            "   • 동영상 생성에는 시간이 소요됩니다\n"
            "   • 구체적인 설명일수록 더 정확한 결과를 얻을 수 있어요!\n"
            "   • 부적절한 내용은 생성되지 않습니다"
        )
        if not update.message:
            return
        await update.message.reply_text(help_message, parse_mode="Markdown")

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        if not update.message:
            return
        await self.clear_session(update.effective_user.id)
        await update.message.reply_text(
            "세션이 초기화되었습니다. 새로운 동영상 생성을 시작할 수 있습니다!"
        )

    async def handle_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        if not update.effective_user:
            return
        if not update.message:
            return
        user_id = update.effective_user.id
        text = str(update.message.text).strip()

        if text.lower() in ["q", "end", "quit"]:
            await self.clear_session(user_id)
            await update.message.reply_text(
                "세션이 종료되었습니다. 새로운 동영상 생성을 시작할 수 있습니다!"
            )
            return

        try:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {"generated_videos": []}

            session = self.user_sessions[user_id]

            processing_message = await update.message.reply_text(
                "🎬 동영상을 생성하고 있습니다...\n\n"
                f"📝 내용: `{text}`\n\n"
                "⏳ 잠시만 기다려주세요!\n"
                "• AI가 최적화된 프롬프트 생성 중...\n"
                "• ByteDance Seedance 모델로 동영상 렌더링 중...\n"
                "• 예상 소요 시간: 1-3분",
                parse_mode="Markdown",
            )

            video_url = self.create_service.create_video(text)
            session["generated_videos"].append(video_url)

            await processing_message.delete()

            await update.message.reply_text(
                f"✨ 동영상이 생성되었습니다!\n\n{video_url}"
            )

        except Exception as e:
            await update.message.reply_text(
                f"❌ 동영상 생성 중 오류가 발생했습니다\n\n"
                f"오류 내용: {str(e)}\n\n"
                f"💡 다시 시도해주세요:\n"
                f"• 다른 텍스트로 시도해보세요\n"
                f"• 너무 복잡한 설명은 피해주세요\n"
                f"• 부적절한 내용이 포함되지 않았는지 확인해주세요"
            )

    async def clear_session(self, user_id):
        if user_id in self.user_sessions:
            self.user_sessions[user_id] = {"generated_videos": []}

    def run(self):

        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
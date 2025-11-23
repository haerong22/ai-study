from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from env import TELEGRAM_BOT_TOKEN


@CrewBase
class ChatBotCrew:

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def communication_agent(self) -> Agent:
        return Agent(config=self.agents_config["communication_agent"])
    
    @task
    def communication_task(self) -> Task:
        return Task(config=self.tasks_config["communication_task"])
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.communication_agent()],
            tasks=[self.communication_task()],
            verbose=True
        )


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message is None or update.message.text is None:
        return 

    user_message = update.message.text

    chatbot_crew = ChatBotCrew()

    result = chatbot_crew.crew().kickoff(inputs={"message": user_message})

    await update.message.reply_text(result.raw)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handler))

app.run_polling()
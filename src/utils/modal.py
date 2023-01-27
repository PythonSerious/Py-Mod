import discord
from src.utils import logger

# logger usage: logger.log("message", logger.logtypes.type)


class Modal:
    def __init__(self, title, questions, action, interaction, user) -> None:
        self.title = title
        self.questions = questions
        self.interaction = interaction
        self.action = action
        self.user = user

    async def fireModal(self, defer_response=True) -> None:
        class Internal(discord.ui.Modal, title=self.title):
            questions = self.questions
            action = self.action
            user = self.user
            defer = defer_response

            for index in range(len(questions)):
                if len(questions) <= 5:
                    locals()[f'q{index + 1}'] = questions[index]

            async def on_submit(self, interaction: discord.Interaction) -> None:
                try:
                    if self.defer:
                        await interaction.response.defer()
                    answers = []
                    for i in range(len(self.questions)):
                        answers.append(getattr(self, f"q{i + 1}").value)
                    return await self.action(interaction, answers, self.user)
                except Exception as e:
                    logger.log(f"36 - modal {str(e)}", logger.logtypes.error)
                    raise e

        if len(self.questions) < 1 or len(self.questions) > 5:
            logger.log("Dynamic Modal: 1 to 5 questions MUST be provided.", logger.logtypes.error)
            return await self.interaction.response.send_message(
                f":x: An invalid amount of questions were provided on the modal.", ephemeral=True)
        await self.interaction.response.send_modal(Internal())

#!/usr/bin/env python
from crewai.flow import Flow, and_, listen, persist, router, start

from conversational_credit_negotiation_flow.agents import (
    classification_agent,
    debt_negotiation_agent,
)
from conversational_credit_negotiation_flow.models import (
    ConversationClassification,
    FlowState,
    Message,
)


@persist()
class ConversationalFlow(Flow[FlowState]):
    @start()
    def clear_state_if_needed(self):
        if getattr(
            getattr(self.state.debt_negotiation, "options", None),
            "clear_history",
            False,
        ):
            self.state.user_message = None
            self.state.assistant_message = None
            self.state.history = []

    @router(clear_state_if_needed)
    def check_if_there_is_a_persona(self):
        if getattr(getattr(self.state.debt_negotiation, "persona", None), None) is None:
            return "no_persona_found"
        else:
            return "persona_found"

    @listen("no_persona_found")
    def no_persona_found(self):
        return {}

    @listen("persona_found")
    def generate_plan(self):
        self.state.debt_negotiation.negotiation_plan = debt_negotiation_agent.kickoff(
            f"""
            Based off of the persona being assessed, generate a negotiation plan for the debt negotiation.

            Persona: {self.state.debt_negotiation.persona}
            """,
        ).pydantic

    @listen("persona_found")
    def classify_user_message(self):
        self.state.debt_negotiation.conversation_classification = (
            classification_agent.kickoff(
                f"""
                Take the latest message being exchanged between the user and the assistant,
                and classify it into a category.

                Latest user message: {self.state.user_message}

                The possible categories are:
                - none: when the conversation hasn't started yet.
                - initial_engagement: when the conversation is just starting - so nothing essential has been discussed yet.
                - in_scope: when the discussion is floating around credits, loans, debt, etc.
                - football: when the discussion is about football, especially about Grêmio or Internacional.
                - out_of_scope: when the discussion is deviating from the topic.
                """,
                response_format=ConversationClassification,
            ).pydantic
        )

    @listen(and_(generate_plan, classify_user_message))
    def respond_to_user(self):
        self.state.assistant_message = debt_negotiation_agent.kickoff(
            f"""
            Based off of the following conversation history and mostly the latest user message,
            respond to the user.

            Conversation history: {self.state.history}
            Latest user message: {self.state.user_message}

            Be mindful of the conversation classification as well as the negotiation plan, trying to steer it towards the appropriate topic.
            However, do not be pushy in case the customer provides a compelling reason to not pay off their debt at this point.

            Conversation classification:
            {self.state.debt_negotiation.conversation_classification}

            Negotiation plan:
            {self.state.debt_negotiation.negotiation_plan}

            This is the customer's persona and financial situation:
            {self.state.debt_negotiation.persona}

            Start conversations by already stating the customer's name, and link it to the negotion plan you have.

            Lastly, make sure to be concise and to the point in your answers, but not too robotic
            or disrespectful.

            EASTER EGG
            ==========
            In case the customer discusses football, particularly about Grêmio or Internacional, use the available tool to
            query Google to know the latest match result, include it in the response and go along with the joke.
            Use queries like "resultados do último jogo do [ADD TEAM HERE]" or something similar.
            However, try to politely steer the conversation back to the topic of debt.
            """,
            response_format=Message,
        ).pydantic

    @listen(respond_to_user)
    def increment_history(self):
        self.state.history.extend(
            [
                msg
                for msg in [self.state.user_message, self.state.assistant_message]
                if msg is not None
            ]
        )

    @listen(increment_history)
    def return_response(self):
        print("=============")
        print(self.state.model_dump())
        print("=============")
        return self.state.model_dump()


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "debt_negotiation": {
                "persona": {
                    "name": "João Cunha",
                    "age": 30,
                    "cellphone": "1234567890",
                    "gender": "male",
                    "debt": 18000,
                    "yearly_revenue": 85000,
                },
                "options": {"clear_history": False},
            }
        }
    )


def plot():
    ConversationalFlow().plot()


if __name__ == "__main__":
    kickoff()

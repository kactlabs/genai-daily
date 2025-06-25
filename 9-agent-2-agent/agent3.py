from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re

@agent(
    name="Email Validator Agent",
    description="Checks if a valid email address is present in the message",
    version="1.0.0"
)
class EmailValidatorAgent(A2AServer):

    @skill(
        name="Check Email",
        description="Validates if the message contains an email address",
        tags=["email", "validation"]
    )
    def check_email(self, text):
        """Checks for a valid email in the input text."""
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(email_regex, text)
        if match:
            return f"Found valid email: {match.group(0)}"
        else:
            return "No valid email address found in the message."

    def handle_task(self, task):
        try:
            input_message = task.message["content"]["text"]
            result = self.check_email(input_message)

            task.artifacts = [{
                "parts": [{"type": "text", "text": result}]
            }]
            task.status = TaskStatus(state=TaskState.COMPLETED)
            return task

        except Exception as e:
            task.artifacts = [{
                "parts": [{"type": "text", "text": f"Error: {e}"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
            return task

# Run the server
if __name__ == "__main__":
    agent = EmailValidatorAgent()
    run_server(agent, port=4752)

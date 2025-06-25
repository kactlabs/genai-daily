from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re

@agent(
    name="Reverse Text Agent",
    description="Reverses the given text",
    version="1.0.0"
)
class ReverseTextAgent(A2AServer):

    @skill(
        name="Reverse Text",
        description="Takes a word or sentence and reverses it",
        tags=["reverse", "text", "string"]
    )
    def reverse_text(self, text):
        """Return the reversed version of the text."""
        return f"The reverse of '{text}' is '{text[::-1]}'"

    def handle_task(self, task):
        try:
            input_message = task.message["content"]["text"]

            # Extract first string of alphabetic words/sentences
            match = re.search(r"[A-Za-z ]{2,}", input_message)
            if not match:
                task.artifacts = [{
                    "parts": [{"type": "text", "text": "Please provide a valid text to reverse."}]
                }]
                task.status = TaskStatus(state=TaskState.FAILED)
                return task

            text_to_reverse = match.group(0).strip()
            reversed_output = self.reverse_text(text_to_reverse)

            task.artifacts = [{
                "parts": [{"type": "text", "text": reversed_output}]
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
    agent = ReverseTextAgent()
    run_server(agent, port=4749)

from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re

@agent(
    name="Palindrome Agent",
    description="Checks if a given word, phrase, or number is a palindrome",
    version="1.0.0"
)
class PalindromeAgent(A2AServer):

    @skill(
        name="Check Palindrome",
        description="Check if the input is a palindrome",
        tags=["palindrome", "text", "string"]
    )
    def is_palindrome(self, input_text):
        cleaned = ''.join(re.findall(r'[A-Za-z0-9]', input_text)).lower()
        if cleaned == cleaned[::-1]:
            return f"'{input_text}' is a palindrome."
        else:
            return f"'{input_text}' is not a palindrome."

    def handle_task(self, task):
        try:
            input_message = task.message["content"]["text"]

            match = re.search(r"[A-Za-z0-9 ]{2,}", input_message)
            if not match:
                task.artifacts = [{
                    "parts": [{"type": "text", "text": "Please provide valid text or number to check."}]
                }]
                task.status = TaskStatus(state=TaskState.FAILED)
                return task

            to_check = match.group(0).strip()
            result = self.is_palindrome(to_check)

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


if __name__ == "__main__":
    agent = PalindromeAgent()
    run_server(agent, port=4750)

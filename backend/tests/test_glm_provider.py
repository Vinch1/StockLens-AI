import os
import sys
from litellm import completion

api_base = "https://api.z.ai/api/coding/paas/v4"
api_key = "11b58f96d9e0460a8e2dd487bd2fef21.vOY2QEoqiZEZ7GQh"

def ask_glm(question: str) -> str:
    response = completion(
        model="zai/glm-5.1",
        api_base=api_base,
        api_key=api_key,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content


def main():
    question = "What is 2 + 2? Answer with only the number."

    try:
        answer = ask_glm(question)
    except Exception as e:
        print("Model call failed:")
        print(e)
        sys.exit(1)

    print("Question:", question)
    print("Answer:", answer)

    if "4" not in answer:
        print("Test failed: expected the answer to contain 4")
        sys.exit(1)

    print("Test passed: GLM answered correctly")


if __name__ == "__main__":
    main()
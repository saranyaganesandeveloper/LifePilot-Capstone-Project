import sys

from gen_client import PRIMARY_MODEL, generate


def main() -> int:
    prompt = "Reply with exactly: Gemini smoke test passed."

    print(f"Configured model: {PRIMARY_MODEL}")
    print("Sending smoke-test prompt...")

    try:
        response = generate(prompt)
    except Exception as exc:
        print(f"Smoke test failed with exception: {exc}")
        return 1

    print("Response:")
    print(response)

    if "failed due to quota or api issues" in response.lower():
        print("Smoke test did not pass because the API request failed.")
        return 1

    print("Smoke test completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

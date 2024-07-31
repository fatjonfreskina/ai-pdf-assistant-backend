# import .env file
from dotenv import load_dotenv
from pdf_assistant import PDFAssistant
import os, sys
load_dotenv()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    client = PDFAssistant(api_key)
    filename = sys.argv[1]
    client.upload_file(filename)

    while True:
          question = input("Enter your question (or type 'exit' to quit): ")
          if question.lower() in ['exit', 'quit']:
            break

          answers = client.get_answers(question)
          for answer in answers:
              print(answer)


if __name__ == '__main__':
    main()
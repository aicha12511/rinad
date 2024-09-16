import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
import openai
import os

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key here
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the path to the PDF file here
PDF_FILE_PATH = 'Policies001 (1).pdf'  # Replace with the actual file path

def extract_text_from_pdf(pdf_path):
    pages_text = []
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        # Iterate through each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pages_text.append(page.get_text())
        pdf_document.close()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return pages_text

def generate_questions(text, num_questions=20):
    max_length = 2000  # Define a reasonable max length for your prompt
    if len(text) > max_length:
        text = text[:max_length]  # Truncate if necessary

    prompt = (
        f"Generate {num_questions} specific questions based on the following text. "
        "The questions should be relevant to the content of the text and avoid asking about versions or structural details. "
        "Ensure that the questions are designed such that the answers can be found within the text provided. "
        "For example, if the text discusses the protection of personal data, questions might include: 'ما هي الضوابط لحماية البيانات الشخصية؟', 'ما هو التعريف لحماية البيانات الشخصية؟', and 'ما هي المواصفات الأساسية لحماية البيانات الشخصية؟'.\n\n"
        f"Text:\n\n{text}\n\n"
        "Questions:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,  # Adjust the number of tokens as needed
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return ""

def main():
    st.title("PDF Question Generator")

    # Use a predefined PDF file path
    pdf_path = PDF_FILE_PATH

    if os.path.exists(pdf_path):
        pages_text = extract_text_from_pdf(pdf_path)
        if pages_text:
            num_pages = st.slider("Select number of pages to process", min_value=1, max_value=len(pages_text), value=len(pages_text), step=1)
            num_questions = st.slider("Select number of questions per page", min_value=1, max_value=100, value=20, step=1)

            if st.button("Generate Questions"):
                all_questions = []
                for page_num in range(num_pages):
                    text = pages_text[page_num]
                    st.write(f"Generating questions for Page {page_num + 1}...")
                    questions = generate_questions(text, num_questions)
                    if questions:
                        all_questions.append(f"Page {page_num + 1}:\n{questions}\n")
                    else:
                        st.write(f"Failed to generate questions for Page {page_num + 1}")

                if all_questions:
                    # Combine all questions into one string
                    all_questions_text = "\n".join(all_questions)
                    
                    st.subheader("Generated Questions:")
                    st.text(all_questions_text)
                    
                    # Convert questions to a text file
                    questions_file = "generated_questions.txt"
                    with open(questions_file, "w", encoding="utf-8") as file:
                        file.write(all_questions_text)
                    
                    # Provide a download button for the text file
                    with open(questions_file, "r", encoding="utf-8") as file:
                        st.download_button(
                            label="Download Questions",
                            data=file,
                            file_name=questions_file,
                            mime="text/plain"
                        )
                else:
                    st.write("No questions were generated.")
        else:
            st.write("No text extracted from the PDF.")
    else:
        st.error(f"The file {pdf_path} does not exist.")

if __name__ == "__main__":
    main()

import os
import time  # Import the time module to introduce delays
import requests  # To make requests to Wolfram Alpha API
import wolframalpha  # Wolfram Alpha API package
from django.shortcuts import render
from dotenv import load_dotenv
import pandas as pd
from .forms import DocumentUploadForm
from .models import UploadedDocument

# Load environment variables from .env file
load_dotenv()

# Get your Wolfram Alpha App ID from the environment
WOLFRAM_ALPHA_APP_ID = os.getenv("WOLFRAM_ALPHA_APP_ID")

# Set the rate limit (delay in seconds between requests)
RATE_LIMIT_DELAY = 1  # 1 second between API requests

def upload_document(request):
    context = {}
    answer = None
    document_content = None  # Initialize the content variable

    if request.method == "POST":
        # Handle document upload
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            
            document = form.save()
            document = form.save()
            context['document_id'] = document.id  # Add this to the context
            context['document_content'] = document_content  # If you're displaying document content
            file_path = document.file.path
            data = pd.read_excel(file_path)  # Extract content from Excel
            context['data_preview'] = data.head().to_html()  # Show document preview in table
            context['document_id'] = document.id  # Pass document ID to use in the question form

            # Save content for future querying (convert the dataframe to a string representation)
            document_content = data.to_string()

        context['form'] = form  # Add form to context so it's displayed on the page
        context['document_content'] = document_content  # Add document content to the context
    else:
        form = DocumentUploadForm()

    return render(request, 'core/upload.html', context)

def ask_question(content, question):
    """
    Use Wolfram Alpha API to answer the user's question based on document content.
    """
    if not WOLFRAM_ALPHA_APP_ID:
        return "Error: Wolfram Alpha App ID is missing."

    try:
        print("Wolfram Alpha App ID:", WOLFRAM_ALPHA_APP_ID)

        # Set up the Wolfram Alpha client
        client = wolframalpha.Client(WOLFRAM_ALPHA_APP_ID)

        # Query Wolfram Alpha
        res = client.query(question)

        # Parse the result
        if res.success:
            answer = next(res.results).text  # Get the direct answer from the first result
            return f"Answer: {answer}"
        else:
            # If there is no result, log and return a message
            return "Sorry, I couldn't find an answer to your question."

    except Exception as e:
        # Capture and print the full exception message
        print("Error occurred in Wolfram Alpha API call:", str(e))
        return f"An error occurred: {str(e)}"

def query_document(request):
    answer = None
    document_content = None
    if request.method == "POST":
        question = request.POST.get("question")
        document_id = request.POST.get("document_id")  # Retrieve document_id from form
        
        if not document_id:
            return render(request, 'core/query.html', {'answer': "Document ID is missing."})
        
        try:
            document_id = int(document_id)  # Ensure it's an integer
            document = UploadedDocument.objects.get(id=document_id)  # Retrieve the document
            document_content = pd.read_excel(document.file.path).to_string()  # Extract content
            
            if not document_content.strip():
                return render(request, 'core/query.html', {'answer': "The document is empty. Please upload a valid document."})

            # Process the question here using Wolfram or other methods
            answer = ask_question(document_content, question)
            
        except UploadedDocument.DoesNotExist:
            answer = "Document not found."
        except ValueError:
            answer = "Invalid document ID."
    
    return render(request, 'core/query.html', {'answer': answer, 'document_content': document_content})

def home(request):
    """
    Render the home page.
    """
    return render(request, 'core/home.html')

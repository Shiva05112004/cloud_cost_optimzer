from app.rag.retriever import retrieve_context
import openai
import os


def build_prompt(question: str, aws_context: dict, retrieved_docs: str) -> str:
    """
    Combines retrieved knowledge + live AWS data + user question
    into a single RAG prompt for the LLM.
    """
    return f"""You are CloudOpt, an intelligent AWS cloud cost optimization assistant.

## Retrieved Knowledge Base Context:
{retrieved_docs}

## Live AWS Data for this account:
- Instance ID     : {aws_context.get('instance_id', 'N/A')}
- Instance Type   : {aws_context.get('instance_type', 'N/A')}
- Average CPU     : {aws_context.get('avg_cpu', 'N/A')}% over 7 days
- Monthly Cost    : ${aws_context.get('monthly_cost', 'N/A')}
- Billing Z-Score : {aws_context.get('z_score', 'N/A')}
- Recommendation  : {aws_context.get('recommendation', 'N/A')}

## User Question:
{question}

## Instructions:
- Answer ONLY based on the retrieved context and live AWS data above.
- Be specific — mention instance IDs, costs, and percentages.
- Give a clear action the user can take right now.
- Keep the answer under 150 words.
"""


def ask_cloudopt(question: str, aws_context: dict) -> str:
    """
    Full RAG pipeline:
    1. Retrieve relevant docs from FAISS
    2. Build grounded prompt with live AWS data
    3. Call LLM and return the answer
    """
    retrieved_docs = retrieve_context(question, k=3)
    prompt         = build_prompt(question, aws_context, retrieved_docs)

    client   = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.2,   # low temp = factual, grounded answers
    )
    return response.choices[0].message.content
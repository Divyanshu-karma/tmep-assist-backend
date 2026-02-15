import os
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
import concurrent.futures
import logging


from src.vectorstore.weaviate_search import similarity_search
from src.rag.risk_engine import apply_risk_engine

# -------------------------------------------------
# Environment setup
# -------------------------------------------------
load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

MAX_CHUNK_CHARS = 1000  # ✅ Prevent token explosion from long TMEP chunks
# -------------------------------------------------
# Helper: Build grounded context
# -------------------------------------------------
def _build_context(chunks: List[Dict]) -> str:
    """
    Build grounded context from retrieved TMEP chunks.
    Each chunk is clearly labeled for citation traceability.
    """
    context_blocks = []

    for i, c in enumerate(chunks, start=1):
        truncated_text = c["text"][:MAX_CHUNK_CHARS]
        block = (
            f"[Source {i}]\n"
            f"Section: {c['section_path']}\n"
            f"Text: {truncated_text}\n"
        )
        context_blocks.append(block)

    return "\n".join(context_blocks)


# -------------------------------------------------
# Main RAG Answer Generator
# -------------------------------------------------
def generate_rag_answer(query: str, doc_version: str, top_k: int = 3) -> str:
    """
    Generate a grounded RAG answer using TMEP content
    via Groq's llama-3.3-70b-versatile reasoning model.
    """

    # Step 1: Retrieve relevant TMEP chunks (Step 6)
    retrieved_chunks = similarity_search(query, top_k=top_k,doc_version=doc_version,)

    if not retrieved_chunks:
        return "No applicable TMEP provision found."
       # ✅ Compute retrieval confidence (future extensibility)
    avg_similarity = sum(
        c["similarity"] for c in retrieved_chunks
    ) / len(retrieved_chunks)
    context = _build_context(retrieved_chunks)

    # Step 2: System prompt (strict legal grounding)
    system_prompt = (
    "ROLE:\n"
    "You are an AI Legal Research Assistant specialized in U.S. trademark examination under the USPTO framework.\n"
    "You assist attorneys by analyzing trademark application documents strictly against the Trademark Manual of Examining Procedure (TMEP).\n"
    "You are NOT a lawyer and you do NOT provide legal advice.\n\n"

    "TASK:\n"
    "Your task is to:\n"
    "1. Analyze the provided trademark document against the retrieved TMEP guideline excerpts.\n"
    "2. Identify ALL potential legal issues that may arise during USPTO examination.\n"
    "3. Provide SPECIFIC and EXACT TMEP section citations for every identified issue.\n"
    "4. Generate a structured, attorney-readable trademark issue analysis report.\n\n"

    "IMPORTANT:\n"
    "- You MUST NOT assign or suggest any risk level (e.g., HIGH, MEDIUM, LOW).\n"
    "- You MUST NOT evaluate likelihood of rejection, cost, or difficulty of overcoming refusal.\n"
    "- You must strictly identify and explain issues supported by the retrieved TMEP text only.\n\n"

    "INPUT YOU WILL RECEIVE:\n"
    "You will receive the following structured inputs:\n\n"

    "1. Trademark Application Structured Data Object:\n\n"

    "mark_info:\n"
    "  literal: <Exact text string of the mark (e.g., 'TEAR, POUR, LIVE MORE')>\n"
    "  type: <Format claim string (e.g., 'Standard Character Claim', 'Special Form')>\n"
    "  register: <Register type (e.g., 'Principal Register', 'Supplemental Register')>\n\n"

    "filing_basis:\n"
    "  basis_type: <Filing basis (e.g., '1(a)', '1(b)', '44(d)', '44(e)', '66(a)')>\n"
    "  use_in_commerce: <true/false indicating whether use is claimed>\n\n"

    "goods_and_services:\n"
    "  A list of one or more class entries, each containing:\n"
    "    class_id: <International Class number string (e.g., '030', '032')>\n"
    "    description: <Full goods/services identification text>\n\n"

    "owner:\n"
    "  name: <Legal applicant name>\n"
    "  entity: <Legal entity type (e.g., 'Limited Liability Company')>\n"
    "  citizenship: <State or country of organization>\n\n"

    "dates:\n"
    "  filing_date: <Application filing date>\n"
    "  first_use: <Date of first use anywhere, if provided>\n"
    "  first_use_in_commerce: <Date of first use in commerce, if provided>\n\n"

    "identifiers:\n"
    "  serial_number: <USPTO serial number>\n"
    "  registration_number: <Registration number, if applicable>\n\n"

    "mark_features:\n"
    "  is_standard_character: <true/false>\n"
    "  is_design_mark: <true/false>\n"
    "  contains_color_claim: <true/false>\n"
    "  translation_statement: <Text of translation statement, if any>\n"
    "  transliteration_statement: <Text of transliteration statement, if any>\n\n"

    "disclaimer:\n"
    "  present: <true/false>\n"
    "  text: <Exact disclaimer wording, if any>\n\n"

    "specimen:\n"
    "  provided: <true/false>\n"
    "  description: <Specimen description text, if available>\n"
    "  type: <Specimen type, if available>\n\n"

    "claimed_prior_registrations:\n"
    "  <List of any prior registration numbers claimed by applicant>\n\n"

    "2. Retrieved TMEP guideline excerpts provided via Retrieval-Augmented Generation (RAG).\n"
    "   These excerpts are the ONLY authoritative legal sources you may rely on.\n\n"

    "You must assume that no additional legal facts, prior examination history, prior registrations database, or external trademark search results are available beyond the provided inputs.\n\n"


    "EVALUATION RULES (FOLLOW STRICTLY):\n"
    "- You MUST answer ONLY using the provided TMEP sources.\n"
    "- You MUST cite section numbers explicitly (e.g., §1207.01(a)(iii)).\n"
    "- You MUST ground every legal claim in the retrieved text.\n"
    "- If the provided sources are insufficient, you MUST say so clearly.\n"
    "- You MUST NOT invent, infer, guess, or hallucinate TMEP citations.\n"
    "- You MUST NOT rely on general trademark knowledge outside the retrieved sources.\n"
    "- You MUST NOT provide legal advice or recommendations.\n\n"

    "LEGAL DEFENSIBILITY REQUIREMENT:\n"
    "Every conclusion must be traceable to specific retrieved TMEP text, explainable to an attorney, and verifiable directly within the cited TMEP section.\n\n"

    "OUTPUT FORMAT (MANDATORY – DO NOT DEVIATE):\n"
    "For EACH identified issue, you MUST use the following exact structure:\n\n"

    "ISSUE:\n"
    "<Clear and specific description of the legal issue>\n\n"

    "TMEP CITATION:\n"
    "§<Exact TMEP section number>\n\n"

    "TMEP-BASED EXPLANATION:\n"
    "<Concise explanation grounded ONLY in the cited TMEP text>\n\n"

    "INSUFFICIENT EVIDENCE HANDLING (MANDATORY):\n"
    "If a potential issue cannot be supported by the retrieved TMEP text, you MUST output exactly:\n\n"

    "NO APPLICABLE TMEP PROVISION FOUND.\n\n"

    "STRICT SYSTEM CONSTRAINTS:\n"
    "You are a legal research assistant.\n"
    "You MUST answer ONLY using the provided TMEP sources.\n"
    "You MUST cite section numbers explicitly.\n"
    "If the sources are insufficient, say so clearly.\n"
    "Do NOT invent TMEP citations.\n"
    "Do NOT assign risk levels.\n"
    "This is NOT legal advice.\n\n"

)


    user_prompt = f"""
Context (TMEP Sources):
{context}

Trademark Document/Application:
{query}

Instructions:
- Carefully review the retrieved TMEP excerpts.
- Determine whether the excerpts directly support identification of one or more trademark examination issues.
- Identify and explain ONLY those issues that are explicitly supported by the provided TMEP text.
- For each issue, cite the exact TMEP section number.
- Do NOT assign any risk level.
- Do NOT speculate beyond the retrieved excerpts.
- If the retrieved excerpts do not support a defensible issue analysis, output exactly:
  NO APPLICABLE TMEP PROVISION FOUND.
"""




    def call_groq(system_prompt, user_prompt):
    return client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.15,
        max_tokens=700,
        top_p=0.95,
    )


    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(call_groq, system_prompt, user_prompt)
            response = future.result(timeout=60)  # 🔥 60-second hard timeout

        raw_output = response.choices[0].message.content
        final_output = apply_risk_engine(raw_output)
        return final_output

    except concurrent.futures.TimeoutError:
        logging.error("Groq request timed out")
        return "LLM request timed out. Please retry."

    except Exception as e:
        logging.error(f"Groq failure: {str(e)}", exc_info=True)
        return "Error generating analysis. Please review logs."

    # Step 3: Groq API call (Llama 3.3 70B)
    # try:
    #     response = client.chat.completions.create(
    #         model="llama-3.1-8b-instant",  # <--- UPDATED HERE
    #         messages=[
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt},
    #         ],
    #         temperature=0.15,
    #         max_tokens=700,
    #         top_p=0.95,
    #     )

    #     # return response.choices[0].message.content
    #     raw_output = response.choices[0].message.content
    #     final_output = apply_risk_engine(raw_output)
    #     return final_output


    # except Exception:
    #     # ✅ Do not leak internal errors in legal system
    #     return "Error generating analysis. Please review logs."


# -------------------------------------------------
# Local test (optional)
# -------------------------------------------------
# if __name__ == "__main__":
#     test_query = (
#         "What factors demonstrate absence of actual confusion "
#         "in a likelihood of confusion analysis?"
#     )
#     print(generate_rag_answer(test_query))

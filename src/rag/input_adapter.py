# # src/rag/input_adapter.py

# def structured_object_to_query(app) -> str:

#     goods_section = ""
#     for cls in sorted(app.goods_map.keys()):
#         desc = app.goods_map[cls]
#         goods_section += f"\nClass {cls}: {desc}"

#     query = (
#         f"Trademark Application Analysis Request:\n\n"
#         f"Mark: {app.mark}\n"
#         f"Mark Type: {app.mark_type}\n"
#         f"Register: {app.register}\n\n"
#         f"Filing Basis: {app.filing_basis}\n"
#         f"Use in Commerce: {app.use_in_commerce}\n\n"
#         f"Owner Name: {app.owner_name}\n"
#         f"Entity Type: {app.owner_entity}\n"
#         f"Citizenship: {app.owner_citizenship}\n\n"
#         f"Serial Number: {app.serial_number}\n"
#         f"Registration Number: {app.registration_number}\n\n"
#         f"Goods and Services:{goods_section}\n\n"
#         f"Analyze the application strictly under TMEP guidelines "
#         f"for potential examination issues."
#     )

#     return query

# src/rag/input_adapter.py

def _safe(val):
    """
    Normalize empty / None fields to prevent embedding noise.
    """
    return val if val not in (None, "", []) else "Not Provided"


def structured_object_to_query(app) -> str:
    """
    Convert structured trademark application object
    into deterministic natural-language query text
    for semantic retrieval.
    """

    # ✅ Deterministic ordering + safe fallback
    goods_section = ""
    goods_map = getattr(app, "goods_map", {}) or {}

    for cls in sorted(goods_map.keys()):
        desc = goods_map[cls]
        goods_section += f"\nClass {cls}: {_safe(desc)}"

    if not goods_section:
        goods_section = "\nNot Provided"

    query = (
        f"Trademark Application Analysis Request:\n\n"
        f"Mark: {_safe(app.mark)}\n"
        f"Mark Type: {_safe(app.mark_type)}\n"
        f"Register: {_safe(app.register)}\n\n"
        f"Filing Basis: {_safe(app.filing_basis)}\n"
        f"Use in Commerce: {_safe(app.use_in_commerce)}\n\n"
        f"Owner Name: {_safe(app.owner_name)}\n"
        f"Entity Type: {_safe(app.owner_entity)}\n"
        f"Citizenship: {_safe(app.owner_citizenship)}\n\n"
        f"Serial Number: {_safe(app.serial_number)}\n"
        f"Registration Number: {_safe(app.registration_number)}\n\n"
        f"Goods and Services:{goods_section}\n\n"
        f"Analyze the application strictly under TMEP guidelines "
        f"for potential examination issues."
    )

    return query

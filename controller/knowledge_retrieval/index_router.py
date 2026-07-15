"""
index_router.py
"""
def route_query_item(index_data: dict, item: dict) -> str:
    """O(1) exact match lookup in learning_index.json. Returns learning_record_id or None."""
    lever = item.get("lever")
    p_name = item.get("parameter_name")
    p_val = str(item.get("parameter_value"))
    f_name = item.get("feature_name")
    
    try:
        record_node = index_data[lever][p_name][p_val][f_name]
        return record_node.get("learning_record_id")
    except KeyError:
        return None

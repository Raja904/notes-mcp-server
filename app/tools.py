from mcp.server import MCPServer
import logging
from app.database import get_connection
from app.auth import get_current_user_id

mcp = MCPServer("multi-user-notes")

@mcp.tool()
async def list_my_notes() -> str:
    """List all notes belonging to the currently authenticated user."""
    user_id = get_current_user_id()
    logging.info(f"Tool call: list_my_notes by user_id {user_id}")
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, title FROM notes WHERE user_id = ?", (user_id,))
    notes = c.fetchall()
    conn.close()
    
    if not notes:
        return "You have no notes."
    
    result = []
    for note in notes:
        result.append(f"ID: {note['id']} | Title: {note['title']}")
    return "\n".join(result)

@mcp.tool()
async def get_note(note_id: int) -> str:
    """Get the full content of a specific note."""
    user_id = get_current_user_id()
    logging.info(f"Tool call: get_note(note_id={note_id}) by user_id {user_id}")
    
    conn = get_connection()
    c = conn.cursor()
    # Authorization: Explicitly check user_id = ? to prevent accessing other users' notes
    c.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    note = c.fetchone()
    conn.close()
    
    if not note:
        logging.warning(f"Authorization failure or not found: user_id {user_id} tried to access note {note_id}")
        return "Error: Note not found or you do not have permission to access it."
    
    return f"Title: {note['title']}\nContent: {note['content']}"

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note for the authenticated user."""
    user_id = get_current_user_id()
    logging.info(f"Tool call: create_note by user_id {user_id}")
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
    conn.commit()
    note_id = c.lastrowid
    conn.close()
    
    return f"Note created successfully with ID: {note_id}"

@mcp.tool()
async def delete_note(note_id: int) -> str:
    """Delete a specific note."""
    user_id = get_current_user_id()
    logging.info(f"Tool call: delete_note(note_id={note_id}) by user_id {user_id}")
    
    conn = get_connection()
    c = conn.cursor()
    # Check existence and ownership first
    c.execute("SELECT id FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    if not c.fetchone():
        conn.close()
        logging.warning(f"Authorization failure or not found: user_id {user_id} tried to delete note {note_id}")
        return "Error: Note not found or you do not have permission to delete it."
        
    c.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    conn.commit()
    conn.close()
    
    return f"Note {note_id} deleted successfully."

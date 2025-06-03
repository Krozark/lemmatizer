import pickle
import os
import sys
import tty
import termios
import lzma
from typing import Dict, Set

def load_data(file_path: str) -> Dict[str, Set[str]]:
    """Load data from pickle file, or return empty dict if file doesn't exist."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            print(f"Warning: Could not load {file_path}, starting with empty data.")
            return {}
    return {}

def save_data(data: Dict[str, Set[str]], file_path: str) -> None:
    """Save data to pickle file."""
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data: {e}")

def get_key():
    """Get a single key press from the user."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        key = sys.stdin.read(1)
        # Handle arrow keys (escape sequences)
        if key == '\x1b':  # ESC sequence
            key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_menu(word: str, lemmas: list, selected_index: int, resolved_count: int, total_ambiguous: int):
    """Display the interactive menu with highlighting."""
    clear_screen()
    
    print("=" * 60)
    print(f"LEMMA DISAMBIGUATION - Progress: {resolved_count}/{total_ambiguous}")
    print("=" * 60)
    print()
    print(f"Word: '{word}'")
    print("Choose the correct lemma:")
    print()
    
    for i, lemma in enumerate(lemmas):
        if i == selected_index:
            # Highlighted option
            print(f"  → \033[7m {i+1}. {lemma} \033[0m")
        else:
            print(f"    {i+1}. {lemma}")
    
    print()
    print("Controls:")
    print("  ↑/↓ : Navigate")
    print("  Enter: Select")
    print("  's': Skip")
    print("  'q': Quit and save")

def interactive_choice(word: str, lemmas: list, resolved_count: int, total_ambiguous: int) -> str:
    """
    Interactive lemma selection with arrow keys.
    
    Returns:
        Selected lemma or special commands ('skip', 'quit')
    """
    lemmas = sorted(lemmas)
    selected_index = 0
    
    while True:
        display_menu(word, lemmas, selected_index, resolved_count, total_ambiguous)
        
        try:
            key = get_key()
            
            if key == '\x1b[A':  # Up arrow
                selected_index = (selected_index - 1) % len(lemmas)
            elif key == '\x1b[B':  # Down arrow
                selected_index = (selected_index + 1) % len(lemmas)
            elif key == '\r' or key == '\n':  # Enter
                return lemmas[selected_index]
            elif key.lower() == 's':
                return 'skip'
            elif key.lower() == 'q':
                return 'quit'
            
        except KeyboardInterrupt:
            return 'quit'

def resolve_ambiguities(data_file:str) -> Dict[str, str]:
    data = load_data(data_file)
    # Print statistics
    print_statistics(data)
    input("Press Enter to start disambiguation...")

    
    # Load existing resolved data if it exists
    resolved_file = data_file.replace('.pkl', '_resolved.pkl')
    resolved_data = load_data(resolved_file)

    # Add unambiguous entries to resolved data
    for word, lemma_set in data.items():
        if len(lemma_set) == 1:
            resolved_data[word] = list(lemma_set)[0]
    
    # Get only ambiguous entries that haven't been resolved yet
    ambiguous_entries = {
        word: lemma_set for word, lemma_set in data.items() 
        if len(lemma_set) > 1 and word not in resolved_data
    }
    
    
    total_ambiguous = len(ambiguous_entries)
    resolved_count = 0
    
    if total_ambiguous == 0:
        print("No ambiguous entries to resolve!")
        return resolved_data
    
    print(f"Found {total_ambiguous} ambiguous entries to resolve.")
    print("Press any key to start...")
    get_key()
    
    try:
        for word, lemma_set in ambiguous_entries.items():
            lemma_list = list(lemma_set)
            
            choice = interactive_choice(word, lemma_list, resolved_count, total_ambiguous)
            
            if choice == 'quit':
                print("\nQuitting and saving progress...")
                break
            elif choice == 'skip':
                print(f"Skipped '{word}'")
                continue
            else:
                resolved_data[word] = choice
                resolved_count += 1
                
                # Save progress after each choice
                save_data(resolved_data, resolved_file)
                
                # Brief confirmation
                clear_screen()
                print(f"✓ '{word}' → '{choice}'")
                print("Saving... Press any key to continue.")
                # get_key()
    
    except KeyboardInterrupt:
        print("\nProcess interrupted. Progress has been saved.")
    
    clear_screen()
    print("=" * 60)
    print("DISAMBIGUATION COMPLETE")
    print("=" * 60)
    print(f"Total resolved entries: {len(resolved_data)}")
    print(f"Ambiguous entries processed: {resolved_count}/{total_ambiguous}")
    
    return resolved_data

def get_ambiguous_entries(data: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """Return only entries with more than one possible lemma."""
    return {word: lemmas for word, lemmas in data.items() if len(lemmas) > 1}

def print_statistics(data: Dict[str, Set[str]]) -> None:
    """Print statistics about the data."""
    total = len(data)
    unambiguous = len([lemmas for lemmas in data.values() if len(lemmas) == 1])
    ambiguous = total - unambiguous
    
    print("=" * 40)
    print("DATA STATISTICS")
    print("=" * 40)
    print(f"Total entries: {total}")
    print(f"Unambiguous: {unambiguous}")
    print(f"Ambiguous: {ambiguous}")
    print(f"Ambiguity rate: {ambiguous/total*100:.1f}%")
    print("=" * 40)

# Example usage
if __name__ == "__main__":
    # Check if running on compatible system
    if os.name != 'posix':
        print("This interactive version requires a POSIX-compatible system (Linux/macOS).")
        print("Use the basic version for Windows.")
        sys.exit(1)
    
    # Resolve ambiguities
    resolved = resolve_ambiguities("fr.pkl")
    
    print(f"\nFinal resolved data:")
    for word, lemma in sorted(resolved.items()):
        print(f"  {word} → {lemma}")
    
    final_data = {k.encode():v.encode() for k,v in resolved.items()}
    with lzma.open("fr.plzma", "wb") as filehandle:
        pickle.dump(final_data, filehandle)

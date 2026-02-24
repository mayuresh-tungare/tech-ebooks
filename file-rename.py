import os
import re
from pathlib import Path

def get_new_name(filepath, mode):
    """Applies the transformation logic to the filename stem only."""
    path = Path(filepath)
    stem = path.stem
    suffix = path.suffix

    if mode == '1': # UPPER CASE
        new_stem = stem.upper()
    elif mode == '2': # lower case
        new_stem = stem.lower()
    elif mode == '3': # Sentence case
        new_stem = stem.capitalize()
    elif mode == '4': # kebab-case
        new_stem = re.sub(r'[\s\._]+', '-', stem).lower()
        new_stem = re.sub(r'-+', '-', new_stem).strip('-')
    elif mode == '5': # snake_case
        new_stem = re.sub(r'[\s\.-]+', '_', stem).lower()
        new_stem = re.sub(r'_+', '_', new_stem).strip('_')
    else:
        return filepath

    return path.with_name(f"{new_stem}{suffix}")

def main():
    session_history = []
    current_script = Path(__file__).name

    while True:
        # 1. Discovery (Recursive)
        all_found = [p for p in Path('.').rglob('*') if p.is_file() and p.name != current_script]
        if not all_found:
            print("\n[!] No files found in this directory or subdirectories.")
            break

        # 2. Filtering by Extension
        print(f"\n--- Total files detected: {len(all_found)} ---")
        ext_filter = input("Filter by extension (e.g. .jpg) or press Enter for ALL: ").strip().lower()
        if ext_filter:
            if not ext_filter.startswith('.'): ext_filter = f".{ext_filter}"
            filtered_files = [f for f in all_found if f.suffix.lower() == ext_filter]
        else:
            filtered_files = all_found

        if not filtered_files:
            print(f"No files matched the filter '{ext_filter}'.")
            continue

        # 3. Format Selection (Moved up to filter out already formatted files)
        print("\nChoose target format:")
        print("1. UPPER CASE | 2. lower case | 3. Sentence case | 4. kebab-case | 5. snake_case")
        mode = input("Select an option (1-5): ").strip()
        if mode not in '12345':
            print("Invalid selection.")
            continue

        # 4. Filter out files already in the requested format
        files_to_process = []
        for f in filtered_files:
            potential_name = get_new_name(f, mode)
            if f.name != potential_name.name:
                files_to_process.append(f)

        if not files_to_process:
            print("\n[✓] All files are already in the requested format. Nothing to do!")
            if input("Try another format? (y/n): ").lower() == 'y': continue
            else: break

        # 5. User Input for Count
        try:
            print(f"\nFound {len(files_to_process)} files that NEED conversion.")
            val = input(f"How many would you like to convert? (1-{len(files_to_process)}): ")
            count = int(val)
            if not (1 <= count <= len(files_to_process)):
                print(f"Error: Range must be 1-{len(files_to_process)}.")
                continue
        except ValueError:
            print("Error: Please enter a valid number.")
            continue

        selected_files = files_to_process[:count]

        # 6. Preview & Confirmation
        preview = []
        print("\n--- Change Preview ---")
        for old_path in selected_files:
            new_path = get_new_name(old_path, mode)
            preview.append((old_path, new_path))
            print(f"{old_path}  ->  {new_path.name}")

        confirm = input("\nProceed with these changes? (y/n): ").lower()
        if confirm != 'y':
            print("Batch cancelled.")
            continue

        # 7. Execution
        current_batch_renames = []
        print("\nRenaming files...")
        for i, (old_path, new_path) in enumerate(preview, 1):
            try:
                if new_path.exists() and old_path != new_path:
                    print(f"[{i}/{count}] Skip: '{new_path.name}' already exists in folder.")
                    continue
                
                old_path.rename(new_path)
                current_batch_renames.append((old_path, new_path))
                print(f"[{i}/{count}] Success: {old_path.name} -> {new_path.name}")
            except Exception as e:
                print(f"[{i}/{count}] Error on {old_path}: {e}")

        # 8. Immediate Undo Option
        if current_batch_renames:
            undo_choice = input("\nBatch complete. Undo these changes immediately? (y/n): ").lower()
            if undo_choice == 'y':
                print("Reverting...")
                for old_p, new_p in reversed(current_batch_renames):
                    try:
                        new_p.rename(old_p)
                    except Exception as e:
                        print(f"Could not revert {new_p.name}: {e}")
                print("Undo successful.")
            else:
                for old_p, new_p in current_batch_renames:
                    session_history.append({"old": str(old_p), "new": str(new_p)})

        if input("\nConvert more files? (y/n): ").lower() != 'y':
            break

    # Final Summary Report
    if session_history:
        print("\n" + "="*85)
        print(f"{'ORIGINAL PATH':<40} | {'NEW PATH':<40}")
        print("-" * 85)
        for item in session_history:
            print(f"{item['old']:<40} | {item['new']:<40}")
        print("="*85)
    
    print("\nExiting. All changes finalized.")

if __name__ == "__main__":
    main()
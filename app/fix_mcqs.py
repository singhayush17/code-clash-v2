"""Script to fix MCQ answer distribution and option ordering.
Shuffles options so correct answer isn't always B and isn't always longest."""
import random
import re
import sys

random.seed(42)  # Reproducible

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all quiz() calls and fix them
    # Pattern: quiz("id", "prompt", "diff", ("tags",), ("opt0","opt1","opt2","opt3"), answer_idx, "explanation")
    pattern = r'(quiz\([^)]*?,\s*\()([^)]+)\),\s*(\d+),'
    
    fixes = 0
    
    def shuffle_options(match):
        nonlocal fixes
        prefix = match.group(1)
        options_str = match.group(2)
        old_idx = int(match.group(3))
        
        # Parse options - they're comma-separated quoted strings
        opts = re.findall(r'"([^"]*)"', options_str)
        if len(opts) != 4:
            return match.group(0)
        
        correct = opts[old_idx]
        
        # Create new shuffled order
        indices = list(range(4))
        # Target: distribute answers roughly equally across 0,1,2,3
        # Use hash of correct answer to deterministically pick new position
        target_positions = [0, 1, 2, 3]
        hash_val = hash(correct) % 4
        
        # Shuffle the wrong answers, place correct at a deterministic position
        wrong = [o for i, o in enumerate(opts) if i != old_idx]
        random.shuffle(wrong)
        
        new_idx = hash_val
        new_opts = list(wrong)
        new_opts.insert(new_idx, correct)
        
        if new_opts == opts and new_idx == old_idx:
            return match.group(0)
        
        fixes += 1
        new_options_str = ','.join(f'"{o}"' for o in new_opts)
        return f'{prefix}{new_options_str}),{new_idx},'
    
    new_content = re.sub(pattern, shuffle_options, content)
    
    if fixes > 0:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f'  Fixed {fixes} questions in {filepath}')
    else:
        print(f'  No fixes needed in {filepath}')

if __name__ == '__main__':
    import glob
    files = glob.glob('app/hld_*.py')
    for f in sorted(files):
        fix_file(f)

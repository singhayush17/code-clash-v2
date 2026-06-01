"""Fix MCQ answer distribution in HLD files.
Reads each file, finds quiz() calls, shuffles option order so correct answer 
is distributed across A/B/C/D and isn't always the longest."""
import re, random, glob, os

random.seed(2026)

def process_file(path):
    with open(path) as f:
        lines = f.readlines()
    
    content = ''.join(lines)
    
    # Find quiz() blocks - each starts with quiz( and ends with ),
    # We need to find the options tuple and answer_index
    # Pattern: (option_tuple), answer_index,
    # The options are 4 strings in a tuple followed by ), int,
    
    changes = 0
    new_lines = list(lines)
    full = ''.join(new_lines)
    
    # Find all patterns like: ("opt1","opt2","opt3","opt4"), N,
    # This appears inside quiz() calls
    pattern = re.compile(
        r'\(("(?:[^"\\]|\\.)*"),\s*("(?:[^"\\]|\\.)*"),\s*("(?:[^"\\]|\\.)*"),\s*("(?:[^"\\]|\\.)*")\),\s*(\d+),',
    )
    
    def replacer(m):
        nonlocal changes
        opts = [m.group(i) for i in range(1,5)]  # quoted strings
        old_idx = int(m.group(5))
        
        correct = opts[old_idx]
        wrong = [o for i,o in enumerate(opts) if i != old_idx]
        
        # Pick a new position based on hash for determinism
        new_idx = (hash(correct) % 4)
        
        random.shuffle(wrong)
        new_opts = list(wrong)
        new_opts.insert(new_idx, correct)
        
        if new_opts == opts and new_idx == old_idx:
            return m.group(0)
        
        changes += 1
        return f'({",".join(new_opts)}),{new_idx},'
    
    new_content = pattern.sub(replacer, full)
    
    if changes:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f'{os.path.basename(path)}: shuffled {changes} questions')
    return changes

total = 0
for path in sorted(glob.glob('app/hld_*.py')):
    if 'fix' in path:
        continue
    total += process_file(path)

print(f'\nTotal: {total} questions reshuffled')

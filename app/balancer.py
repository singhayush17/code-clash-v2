import dataclasses
import hashlib

def balance_task(task):
    if not hasattr(task, "options") or not task.options:
        return task
    if not hasattr(task, "answer_index") or task.answer_index is None:
        return task
    if len(task.options) != 4:
        return task
        
    h = int(hashlib.md5(task.id.encode('utf-8')).hexdigest(), 16)
    target_idx = h % 4
    
    old_correct_idx = task.answer_index
    new_options = list(task.options)
    
    if old_correct_idx != target_idx:
        new_options[old_correct_idx], new_options[target_idx] = new_options[target_idx], new_options[old_correct_idx]
        
    final_options = tuple(new_options) if isinstance(task.options, tuple) else new_options
    return dataclasses.replace(task, options=final_options, answer_index=target_idx)

def balance_lesson(lesson):
    if not hasattr(lesson, "tasks") or not lesson.tasks:
        return lesson
        
    new_tasks = []
    quiz_tasks = [t for t in lesson.tasks if hasattr(t, "options") and t.options and len(t.options) == 4 and getattr(t, "answer_index", None) is not None]
    
    quiz_positions = {t.id: idx for idx, t in enumerate(quiz_tasks)}
    
    for task in lesson.tasks:
        if task.id in quiz_positions:
            pos = quiz_positions[task.id]
            target_idx = pos % 4
            
            old_correct_idx = task.answer_index
            new_options = list(task.options)
            
            if old_correct_idx != target_idx:
                new_options[old_correct_idx], new_options[target_idx] = new_options[target_idx], new_options[old_correct_idx]
                
            final_options = tuple(new_options) if isinstance(task.options, tuple) else new_options
            updated_task = dataclasses.replace(task, options=final_options, answer_index=target_idx)
            new_tasks.append(updated_task)
        else:
            new_tasks.append(task)
            
    final_tasks = tuple(new_tasks) if isinstance(lesson.tasks, tuple) else new_tasks
    return dataclasses.replace(lesson, tasks=final_tasks)

def balance_lessons(lessons):
    return [balance_lesson(lesson) for lesson in lessons]

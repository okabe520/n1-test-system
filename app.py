import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import (
    init_db, get_exam_questions, get_questions_by_section,
    save_result, get_history, get_result, get_question_count,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'n1-test-secret-key'

@app.template_filter('parse_json')
def parse_json_filter(s):
    return json.loads(s)

init_db()

EXAM_TIME_SECONDS = 110 * 60

SECTION_NAMES = {
    'vocab': '言語知識（文字・語彙）',
    'grammar': '文法',
    'reading': '読解',
}

TYPE_NAMES = {
    'yomikata': '漢字読み',
    'context': '文脈規定',
    'paraphrase': '言い換え',
    'usage': '用法',
    'form': '文法形式判断',
    'order': '文章組合',
    'text_grammar': '文章文法',
    'short': '内容理解（短文）',
    'medium': '内容理解（中文）',
    'long': '内容理解（長文）',
    'integrated': '統合理解',
    'opinion': '主張理解',
    'search': '情報検索',
}


@app.route('/')
def index():
    count = get_question_count()
    history = get_history(5)
    return render_template('index.html', count=count, history=history)


@app.route('/exam')
def exam():
    questions = get_exam_questions()
    if not questions:
        return '题库不足，请先运行 seed_questions.py', 500
    return render_template('exam.html', questions=questions,
                           total_time=EXAM_TIME_SECONDS,
                           section_names=SECTION_NAMES,
                           type_names=TYPE_NAMES)


@app.route('/practice')
def practice():
    return render_template('practice.html', section_names=SECTION_NAMES)


@app.route('/api/practice/<section>')
def api_practice(section):
    count = request.args.get('count', 10, type=int)
    questions = get_questions_by_section(section, limit=count)
    return jsonify(questions)


@app.route('/api/check', methods=['POST'])
def api_check():
    data = request.json
    qid = data['question_id']
    user_answer = data['answer']
    from database import get_db
    with get_db() as conn:
        q = conn.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
    if not q:
        return jsonify({'error': 'not found'}), 404
    correct = (user_answer == q['answer'])
    return jsonify({
        'correct': correct,
        'correct_answer': q['answer'],
        'explanation': q['explanation'],
    })


@app.route('/api/submit-exam', methods=['POST'])
def api_submit_exam():
    data = request.json
    answers = data.get('answers', {})
    duration = data.get('duration', 0)
    total = len(answers)
    correct = 0
    details = []
    from database import get_db
    with get_db() as conn:
        for qid_str, user_ans in answers.items():
            qid = int(qid_str)
            q = conn.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
            is_right = (user_ans == q['answer']) if q else False
            if is_right:
                correct += 1
            details.append({
                'id': qid,
                'user_answer': user_ans,
                'correct_answer': q['answer'] if q else -1,
                'is_correct': is_right,
                'question_text': q['question_text'] if q else '',
                'options': json.loads(q['options']) if q else [],
                'explanation': q['explanation'] if q else '',
            })
    score = round(correct / total * 100) if total > 0 else 0
    save_result('exam', score, total, correct, duration, json.dumps(details, ensure_ascii=False))
    return jsonify({
        'score': score, 'total': total, 'correct': correct,
        'details': details,
    })


@app.route('/api/submit-practice-result', methods=['POST'])
def api_submit_practice_result():
    data = request.json
    save_result(
        'practice', data['score'], data['total'],
        data['correct'], data.get('duration', 0),
        json.dumps(data.get('details', []), ensure_ascii=False)
    )
    return jsonify({'ok': True})


@app.route('/result/<int:result_id>')
def view_result(result_id):
    r = get_result(result_id)
    if not r:
        return 'Not found', 404
    r = dict(r)
    r['details'] = json.loads(r['details'])
    return render_template('result.html', result=r, type_names=TYPE_NAMES)


@app.route('/history')
def history():
    rows = get_history(50)
    return render_template('history.html', history=rows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

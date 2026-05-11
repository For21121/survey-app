const totalQuestions = 10; let currentQuestion = 1;
function updateProgress() { document.getElementById('progressFill').style.width = (currentQuestion/totalQuestions*100) + '%'; }
function nextQuestion(id) {
    const block = document.getElementById('q'+id);
    const inputs = block.querySelectorAll('input[type="radio"], input[type="text"], input[type="number"], textarea');
    let hasAnswer = false;
    for (let inp of inputs) { if (inp.type=='radio') { if(inp.checked) hasAnswer=true; } else { if(inp.value.trim()) hasAnswer=true; } }
    if (block.querySelectorAll('input[type="checkbox"]').length > 0) hasAnswer = true;
    if (!hasAnswer) { alert('Пожалуйста, ответьте на вопрос'); return; }
    block.style.display='none'; currentQuestion++; document.getElementById('q'+(id+1)).style.display='block'; updateProgress(); window.scrollTo(0,0);
}
function prevQuestion(id) { document.getElementById('q'+id).style.display='none'; currentQuestion--; document.getElementById('q'+(id-1)).style.display='block'; updateProgress(); window.scrollTo(0,0); }
updateProgress();

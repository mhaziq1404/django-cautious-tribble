function scrollToBottom(time=0) {
    setTimeout(function() {
        const container = document.getElementById('chat_container');
        container.scrollTop = container.scrollHeight;
    }, time);
}
scrollToBottom()

document.addEventListener('DOMContentLoaded', function() {
    const chatbox = document.getElementById('chatbox');
    const toggleButton = document.getElementById('chatbox-toggle');

    toggleButton.addEventListener('click', function() {
        if (chatbox.classList.contains('hidden')) {
            chatbox.classList.remove('hidden');
            chatbox.classList.add('show');
        } else {
            chatbox.classList.remove('show');
            chatbox.classList.add('hidden');
        }
    });
});

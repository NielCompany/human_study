// 드래그 이동 기능 + 위치 기억
function dragElement(elmnt, handle) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  
    if (handle) {
      handle.onmousedown = dragMouseDown;
    }
  
    function dragMouseDown(e) {
      e.preventDefault();
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      document.onmousemove = elementDrag;
    }
  
    function elementDrag(e) {
      e.preventDefault();
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
  
      elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
      elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
      elmnt.style.bottom = "auto";
      elmnt.style.right = "auto";
  
      // 위치 기억
      localStorage.setItem("chatbox_top", elmnt.style.top);
      localStorage.setItem("chatbox_left", elmnt.style.left);
    }
  
    function closeDragElement() {
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }
  
  // 챗봇 열기/닫기 토글 (상태 기억)
  function toggleChat() {
    const box = document.getElementById("chat-box");
    const toggleBtn = document.getElementById("chatbot-toggle");
    const isHidden = box.style.display === "none" || box.style.display === "";
  
    if (isHidden) {
      box.style.display = "flex";
      toggleBtn.style.display = "none";
      localStorage.setItem("chat_open", "true");
    } else {
      box.style.display = "none";
      toggleBtn.style.display = "block";
      localStorage.setItem("chat_open", "false");
    }
  }
  
  // 메시지 전송
  async function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;
  
    const chatLog = document.getElementById("chat-messages");
    chatLog.innerHTML += `<div class="chat user">${message}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  
    input.value = "";
    localStorage.setItem("chat_input", ""); // 초기화
  
    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
  
      const data = await response.json();
      chatLog.innerHTML += `<div class="chat bot"> ${data.reply}</div>`;
      chatLog.scrollTop = chatLog.scrollHeight;
  
      // 로그 저장
      localStorage.setItem("chat_log", chatLog.innerHTML);
    } catch (error) {
      chatLog.innerHTML += `<div class="chat bot">오류가 발생했습니다.</div>`;
    }
  }
  
  // 초기 설정
  document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const chatHeader = document.getElementById("chat-header");
    const input = document.getElementById("chat-input");
  
    dragElement(chatBox, chatHeader);
  
    // 대화, 입력창, 위치, 상태 복원
    document.getElementById("chat-messages").innerHTML = localStorage.getItem("chat_log") || "";
    input.value = localStorage.getItem("chat_input") || "";
  
    const top = localStorage.getItem("chatbox_top");
    const left = localStorage.getItem("chatbox_left");
    if (top && left) {
      chatBox.style.top = top;
      chatBox.style.left = left;
      chatBox.style.bottom = "auto";
      chatBox.style.right = "auto";
    }
  
    const open = localStorage.getItem("chat_open");
    if (open === "true") {
      chatBox.style.display = "flex";
      document.getElementById("chatbot-toggle").style.display = "none";
    }
  
    // 엔터 키 입력 전송
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  
    // 입력값 저장
    input.addEventListener("input", () => {
      localStorage.setItem("chat_input", input.value);
    });
  
    // 전송 버튼 연결
    const sendBtn = document.querySelector(".chat-input-area button");
    if (sendBtn) sendBtn.addEventListener("click", sendMessage);
  });

    // 브라우저 종료 후 재접속 시 대화 로그 삭제
    document.addEventListener("DOMContentLoaded", function () {
    const isReturning = !sessionStorage.getItem("chat_session_active");
    sessionStorage.setItem("chat_session_active", "true");

    if (isReturning) {
      clearChatData();
    }
  });

  // chat bot 초기화 
  function clearChatData() {
  localStorage.removeItem("chat_log");
  localStorage.removeItem("chat_input");
  localStorage.removeItem("chatbox_top");
  localStorage.removeItem("chatbox_left");
  localStorage.removeItem("chat_open");
}



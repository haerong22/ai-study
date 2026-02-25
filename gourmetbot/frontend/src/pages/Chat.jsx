import React, { useState, useEffect, useRef } from "react";
import { sendMessagesToServer } from "../sendMessageToServer.js";
import restaurantImage from '../assets/go.png';
import { 
  Bot, 
  Send, 
  ArrowLeft, 
  MoreVertical, 
  Utensils,  
  Loader2,
  Sparkles,
  AlertCircle
} from "lucide-react";

/**
 * ------------------------------------------------------------------
 * [스타일 상수]
 * ------------------------------------------------------------------
 */
const STYLES = {
  container: "min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col items-center justify-center relative overflow-hidden",
  card: "w-full max-w-md bg-white h-[100dvh] md:h-[800px] md:max-h-[90vh] md:rounded-[2rem] md:shadow-2xl flex flex-col overflow-hidden transition-all duration-300 relative border border-slate-100",
  primaryButton: "bg-slate-900 hover:bg-slate-800 text-white px-6 py-3 rounded-full font-medium transition-all active:scale-95 flex items-center gap-2 shadow-lg shadow-slate-900/20",
  iconButton: "p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500 hover:text-slate-900",
  bubbleUser: "bg-slate-900 text-white rounded-2xl rounded-tr-sm px-5 py-3 max-w-[85%] self-end shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300",
  bubbleBot: "bg-slate-100 text-slate-800 rounded-2xl rounded-tl-sm px-5 py-3 max-w-[85%] self-start shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300",
  bubbleError: "bg-red-50 text-red-600 border border-red-100 rounded-2xl px-5 py-3 max-w-[85%] self-center text-sm flex items-center gap-2 animate-in fade-in",
  inputArea: "p-4 bg-white/80 backdrop-blur-md border-t border-slate-100",
  inputField: "w-full bg-slate-100 border-none focus:ring-2 focus:ring-slate-900/10 rounded-full pl-5 pr-12 py-3.5 text-sm transition-all placeholder:text-slate-400 outline-none",
};

/**
 * ------------------------------------------------------------------
 * [메인 컴포넌트]
 * ------------------------------------------------------------------
 */
export default function App() {
  const [screen, setScreen] = useState("home"); // 'home' | 'chat'
  const [conversationId, setConversationId] = useState(null);
  
  // 초기 메시지 상태
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "bot",
      text: "안녕하세요! GourmetBot입니다. \n 👨‍🍳 예약을 도와 드리겠습니다.",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  // 채팅 시작 시 랜덤한 Conversation ID 생성 (또는 필요한 로직으로 대체)
  const goToChat = () => {
    // 예: 현재 시간 + 랜덤 숫자로 임시 ID 생성 (실무에서는 UUID 추천)
    const newId = `conv_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    setConversationId(newId);
    setScreen("chat");
  };

  const goToHome = () => {
    setScreen("home");
    // 대화방을 나가면 ID를 초기화하거나 유지할지 결정 (여기선 유지)
  };

  return (
    <div className={STYLES.container}>
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-orange-200/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-0%] right-[-10%] w-[40%] h-[40%] bg-blue-200/20 rounded-full blur-[100px] pointer-events-none" />

      <div className={STYLES.card}>
        {screen === "home" ? (
          <HomeView onStart={goToChat} />
        ) : (
          <ChatView 
            messages={messages} 
            setMessages={setMessages} 
            onBack={goToHome}
            conversationId={conversationId} // ID 전달
          />
        )}
      </div>
      
      <p className="hidden md:block mt-6 text-slate-400 text-sm font-medium flex items-center gap-2">
        <Sparkles size={14} /> GourmetBot AI Chat System
      </p>
    </div>
  );
}

/**
 * [홈 화면]
 */
function HomeView({ onStart }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-8 animate-in fade-in duration-500">
      <div className="relative">
        <div className="absolute inset-0 bg-orange-100 rounded-full blur-xl animate-pulse"></div>
        <div className="relative bg-white p-2 rounded-[2rem] shadow-xl shadow-orange-100/50 overflow-hidden">
          <img src={restaurantImage} alt="Restaurant" className="w-32 h-32 object-cover rounded-[1.5rem]" />
        </div>
      </div>
      
      <div className="space-y-3">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Gourmet<span className="text-orange-500">Bot</span>
        </h1><div className="flex items-center justify-center gap-2"> {/* 구분선 추가 */}
          <div className="h-px bg-slate-300 w-12"></div>
          <p className="text-lg font-serif text-orange-500 leading-relaxed"> {/* 색상, 글꼴, 크기 변경 */}
            The Spring Welcome.
          </p>
          <div className="h-px bg-slate-300 w-12"></div>
        </div>
        <p className="text-slate-500 max-w-[240px] mx-auto leading-relaxed">
          AI가 예약을 도와드립니다!
        </p>
      </div>

      <button onClick={onStart} className={STYLES.primaryButton}>
        <Utensils size={18} />
        <span>예약 시작하기</span>
      </button>

      <div className="absolute bottom-8 text-xs text-slate-400 font-medium">
        Powered by OpenAI & React
      </div>
    </div>
  );
}

/**
 * [채팅 화면] - 실제 API 연동 부분
 */
function ChatView({ messages, setMessages, onBack, conversationId }) {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  // 자동 스크롤
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // 1. 사용자 메시지 즉시 UI에 추가
    const userMsg = {
      id: Date.now(),
      role: "user",
      text: input,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input; // API 요청용으로 저장
    setInput("");
    setIsTyping(true);

    try {
      // 2. [서버 연동] 실제 API 호출
      // sendMessagesToServer 함수 사용
      const data = await sendMessagesToServer(currentInput, conversationId);

      // 3. 서버 응답 처리
      // 서버 응답 구조에 따라 data.message, data.answer 등 필드를 조정해야 할 수 있습니다.
      // 여기서는 data가 텍스트 자체라고 가정하거나, 객체라면 JSON.stringify로 보여줍니다.
      const botResponseText = typeof data === 'string' ? data : JSON.stringify(data);

      const botMsg = {
        id: Date.now() + 1,
        role: "bot",
        text: botResponseText || "응답이 비어있습니다.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);

    } catch (error) {
      console.error("API Error:", error);
      
      // 에러 발생 시 UI 표시
      const errorMsg = {
        id: Date.now() + 1,
        role: "error", // 에러 타입 추가
        text: "서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      {/* 헤더 */}
      <div className="px-4 py-4 border-b border-slate-100 flex items-center justify-between bg-white/80 backdrop-blur-sm z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className={STYLES.iconButton}>
            <ArrowLeft size={20} />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-orange-600">
              <Bot size={20} />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900">GourmetBot AI</h3>
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${isTyping ? "bg-orange-500 animate-pulse" : "bg-green-500"}`}></span>
                <span className="text-xs text-slate-400 font-medium">
                  {isTyping ? "입력 중..." : "답변 가능"}
                </span>
              </div>
            </div>
          </div>
        </div>
        <button className={STYLES.iconButton}>
          <MoreVertical size={20} />
        </button>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-white scrollbar-hide">
        <div className="text-center text-xs text-slate-300 py-4">
          대화 ID: {conversationId}
        </div>
        
        {messages.map((msg) => {
          if (msg.role === "error") {
            return (
              <div key={msg.id} className={STYLES.bubbleError}>
                <AlertCircle size={16} />
                {msg.text}
              </div>
            );
          }
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
<div className={msg.role === "user" ? STYLES.bubbleUser : STYLES.bubbleBot}>
  <span className="whitespace-pre-wrap text-sm leading-relaxed block">
    {msg.text}
  </span>
</div>
              <span className="text-[10px] text-slate-400 mt-1 px-1">
                {msg.time}
              </span>
            </div>
          );
        })}

        {isTyping && (
          <div className="flex items-center gap-2 text-slate-400 text-sm ml-2 animate-pulse">
            <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
              <Loader2 size={14} className="animate-spin" />
            </div>
            <span className="text-xs">답변 생성 중...</span>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* 입력 영역 */}
      <div className={STYLES.inputArea}>
        <form onSubmit={handleSend} className="relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="메시지를 입력하세요..."
            className={STYLES.inputField}
            disabled={isTyping} // 전송 중 입력 방지
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className={`absolute right-2 p-2 rounded-full transition-all ${
              input.trim() && !isTyping
                ? "bg-slate-900 text-white shadow-md hover:bg-slate-800" 
                : "bg-transparent text-slate-300 cursor-not-allowed"
            }`}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </>
  );
}
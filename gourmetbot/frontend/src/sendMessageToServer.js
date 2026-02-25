import axios from 'axios';
/**
 * ------------------------------------------------------------------
 * [API 설정]
 * 사용자분께서 제공해주신 서버 연동 로직입니다.
 * ------------------------------------------------------------------
 */
const baseURL = "http://localhost:8081/api/v1";

export const sendMessagesToServer = async (message, conversationId) => {
  // 서버가 { "message" : "요청메세지" } 형태의 JSON body를 기대하므로,
  // message를 객체 형태로 감싸서 전송합니다.
  const response = await axios.post(`${baseURL}/chat`, { message: message }, {
    headers: {
      // ConversationId 헤더는 그대로 유지합니다.
      ConversationId: conversationId,
    },
  });

  return response.data;
};
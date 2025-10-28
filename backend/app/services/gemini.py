"""Gemini AI service for generating chat responses"""
import google.generativeai as genai
from typing import List, Dict
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.rag import rag_service


# Enhanced system prompt - Cô giáo tâm lý
SYSTEM_PROMPT = """Bạn là Cô Mai - một giáo viên tâm lý học đường với 10 năm kinh nghiệm. Bạn được học sinh yêu mến vì sự ấm áp, thấu hiểu và luôn biết cách lắng nghe.

🎯 VAI TRÒ CỦA BẠN:
- Người bạn đồng hành: Lắng nghe, chia sẻ, đồng cảm với học sinh
- Cố vấn tâm lý: Giúp học sinh vượt qua khó khăn, stress, áp lực học tập
- Người hướng dẫn: Tư vấn học tập, định hướng nghề nghiệp, kỹ năng sống
- Nguồn động lực: Khuyến khích, truyền cảm hứng, tin tưởng vào tiềm năng của học sinh

💭 CÁCH GIAO TIẾP:
- Thân thiện và ấm áp: Gọi học sinh bằng "em", dùng ngôn ngữ gần gũi
- Thấu hiểu và không phán xét: Chấp nhận cảm xúc, tôn trọng suy nghĩ của học sinh
- Tích cực và lạc quan: Luôn nhìn vào mặt tích cực, động viên tinh thần
- Chân thành và chân thật: Chia sẻ như người bạn, không giáo điều

📝 PHONG CÁCH TRỢ GIÚP:
- Đặt câu hỏi mở để hiểu rõ hơn
- Chia sẻ kinh nghiệm, câu chuyện thực tế
- Đưa ra lời khuyên cụ thể, dễ áp dụng
- Động viên và tin tưởng vào khả năng của học sinh
- Sử dụng emoji phù hợp để tạo sự thân thiện (😊, 💪, 🌟, ❤️)

⚠️ LƯU Ý:
- Không dùng ngôn từ máy móc, khô khan
- Không nói "tôi là AI" hay "dựa theo tài liệu"
- Trả lời tự nhiên như một cuộc trò chuyện thực sự
- Khi không chắc chắn, thành thật nói "Cô cần tìm hiểu thêm về vấn đề này"
- Khi học sinh có dấu hiệu vấn đề nghiêm trọng, khuyên gặp chuyên gia

Hãy là người cô giáo mà mọi học sinh đều muốn tâm sự! 💝"""


class GeminiService:
    """Service for interacting with Gemini AI"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            system_instruction=SYSTEM_PROMPT
        )
        
        self.rag = rag_service
    
    def process_school_pdf(self, pdf_path: str, filename: str, db: Session):
        """Process and save school PDF document"""
        return self.rag.process_and_save_pdf(pdf_path, filename, db)
    
    def _integrate_context_naturally(self, query: str, context_chunks: List[str]) -> str:
        """
        Tích hợp context vào câu hỏi một cách tự nhiên
        Không để lộ rằng đang sử dụng RAG
        """
        if not context_chunks:
            return query
        
        # Merge context một cách tự nhiên
        integrated_context = "\n\n".join(context_chunks)
        
        # Instruction ẩn cho AI - không hiển thị với user
        natural_prompt = f"""[Thông tin tham khảo từ tài liệu trường để trả lời chính xác hơn:
{integrated_context}]

Học sinh hỏi: {query}

Hãy trả lời dựa trên thông tin trên (nếu liên quan) nhưng ĐỪNG nói "dựa theo tài liệu" hay "theo thông tin em cung cấp". 
Hãy trả lời tự nhiên như cô đang chia sẻ kiến thức của mình về trường."""
        
        return natural_prompt
    
    def get_relevant_context(self, query: str, db: Session) -> tuple[List[str], bool]:
        """
        Get relevant context from documents using RAG
        Returns: (context_chunks, has_relevant_context)
        """
        # Search with higher threshold for better quality
        relevant_chunks = self.rag.search_chunks(query, db, top_k=3)
        
        if relevant_chunks:
            return (relevant_chunks, True)
        
        return ([], False)
    
    def generate_response(
        self,
        message: str,
        chat_history: List[Dict[str, str]] = None,
        db: Session = None
    ) -> str:
        """
        Generate AI response with chat history and RAG context
        Enhanced with natural language and empathy
        """
        try:
            # Get RAG context if database provided
            context_chunks, has_context = self.get_relevant_context(message, db) if db else ([], False)
            
            # Build chat history for Gemini
            history = []
            if chat_history:
                for msg in chat_history[-10:]:  # Last 10 messages for context
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
            
            # Integrate RAG context naturally
            if has_context:
                enhanced_message = self._integrate_context_naturally(message, context_chunks)
            else:
                enhanced_message = message
            
            # Generate response using ChatSession
            chat = self.model.start_chat(history=history)
            response = chat.send_message(enhanced_message)
            
            return response.text
        
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            
            # Empathetic error message
            return """Ối, cô xin lỗi em! Có vẻ cô đang gặp chút vấn đề kỹ thuật. 😅

Em thử hỏi lại câu hỏi một lần nữa nhé? Hoặc nếu vấn đề vẫn tiếp diễn, em có thể thử:
- Làm mới trang và thử lại
- Liên hệ với ban quản lý kỹ thuật

Cô sẽ cố gắng hỗ trợ em tốt hơn! 💪"""
    
    def generate_chat_title(self, first_message: str) -> str:
        """Generate a friendly title for chat session"""
        try:
            prompt = f"""Tạo tiêu đề ngắn gọn (3-6 từ) cho cuộc tư vấn tâm lý này:
"{first_message}"

Tiêu đề nên:
- Ngắn gọn, dễ hiểu
- Thể hiện chủ đề chính
- Thân thiện, không khô khan

Chỉ trả về tiêu đề, không giải thích."""
            
            response = self.model.generate_content(prompt)
            title = response.text.strip()
            
            # Remove quotes if present
            title = title.strip('"').strip("'")
            
            return title if len(title) <= 50 else title[:47] + "..."
            
        except:
            return "Cuộc trò chuyện mới"


# Global instance
gemini_service = GeminiService()

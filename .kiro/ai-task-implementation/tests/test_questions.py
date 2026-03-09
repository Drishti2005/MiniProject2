"""
Tests for question suggestion functionality.
"""

import pytest
from unittest.mock import Mock, patch
from gemini_service import GeminiService


class TestSuggestQuestions:
    """Test question suggestion generation."""
    
    @pytest.mark.asyncio
    async def test_suggest_with_sufficient_context(self):
        """Test question generation with sufficient context."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "What are the side effects of this medication?",
                "How long until I feel better?",
                "Do I need to follow up?"
            ]
        }
        '''
        
        transcript = " ".join(["word"] * 60)  # 60 words for sufficient context
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            assert len(result) == 3
            assert all(isinstance(q, str) for q in result)
            assert all("?" in q for q in result)
    
    @pytest.mark.asyncio
    async def test_suggest_with_minimal_context(self):
        """Test question generation with minimal context."""
        service = GeminiService(api_key="test_api_key_12345")
        
        # Less than 50 words
        transcript = "Doctor said take medicine"
        
        result = await service.suggest_questions(transcript)
        
        # Should return empty list due to insufficient context
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_suggest_with_empty_transcript(self):
        """Test question generation with empty transcript."""
        service = GeminiService(api_key="test_api_key_12345")
        
        result = await service.suggest_questions("")
        assert len(result) == 0
        
        result = await service.suggest_questions("   ")
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_suggest_limits_to_three_questions(self):
        """Test that questions are limited to 3."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "Question 1?",
                "Question 2?",
                "Question 3?",
                "Question 4?",
                "Question 5?"
            ]
        }
        '''
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            # Should limit to 3 questions
            assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_suggest_prompt_formatting(self):
        """Test that prompt is properly formatted."""
        service = GeminiService(api_key="test_api_key_12345")
        
        transcript = " ".join(["word"] * 60)
        
        mock_response = Mock()
        mock_response.text = '{"questions": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response) as mock_gen:
            await service.suggest_questions(transcript)
            
            # Verify the prompt contains the transcript
            call_args = mock_gen.call_args[0][0]
            assert transcript in call_args
            assert "patient advocate" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_filters_invalid_questions(self):
        """Test filtering of invalid questions."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "Valid question?",
                "",
                "   ",
                123,
                null,
                "Another valid question?"
            ]
        }
        '''
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            # Should only include valid string questions
            assert len(result) == 2
            assert "Valid question?" in result
            assert "Another valid question?" in result
    
    @pytest.mark.asyncio
    async def test_suggest_response_time(self):
        """Test question generation completes within 2 seconds."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"questions": ["Question?"]}'
        
        transcript = " ".join(["word"] * 60)
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.suggest_questions(transcript)
            elapsed = time.time() - start
            
            assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_suggest_with_changing_topics(self):
        """Test question generation with changing conversation topics."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "What about the new symptom?",
                "Should I stop the old medication?"
            ]
        }
        '''
        
        transcript = " ".join([
            "First we discussed blood pressure.",
            "Now we're talking about diabetes.",
            "The patient has new symptoms."
        ])
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            assert len(result) >= 2
            # Questions should be relevant to current context
            assert any("new" in q.lower() or "symptom" in q.lower() for q in result)
    
    @pytest.mark.asyncio
    async def test_suggest_error_handling(self):
        """Test error handling returns empty list."""
        service = GeminiService(api_key="test_api_key_12345")
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service, '_call_api_with_retry', side_effect=Exception("API Error")):
            result = await service.suggest_questions(transcript)
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_suggest_handles_missing_questions_field(self):
        """Test handling of response missing questions field."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"suggestions": []}'  # Wrong field name
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            assert result == []


class TestQuestionProperties:
    """Property-based tests for question suggestions."""
    
    @pytest.mark.asyncio
    async def test_property_question_cardinality(self):
        """
        Property 11: For any request with sufficient context, 2-3 questions returned.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "Question 1?",
                "Question 2?",
                "Question 3?"
            ]
        }
        '''
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            # Should return 2-3 questions
            assert 2 <= len(result) <= 3
    
    @pytest.mark.asyncio
    async def test_property_question_transmission_time(self):
        """
        Property 12: Question suggestions sent within 2 seconds.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"questions": ["Question?"]}'
        
        transcript = " ".join(["word"] * 60)
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.suggest_questions(transcript)
            elapsed = time.time() - start
            
            assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_property_questions_are_strings(self):
        """Property: All questions must be non-empty strings."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "questions": [
                "Question 1?",
                "Question 2?"
            ]
        }
        '''
        
        transcript = " ".join(["word"] * 60)
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.suggest_questions(transcript)
            
            for question in result:
                assert isinstance(question, str)
                assert len(question.strip()) > 0

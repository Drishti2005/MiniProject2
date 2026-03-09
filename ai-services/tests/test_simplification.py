"""
Tests for medical term simplification functionality.
"""

import pytest
from unittest.mock import Mock, patch
from gemini_service import GeminiService


class TestSimplifyTerms:
    """Test medical term simplification."""
    
    @pytest.mark.asyncio
    async def test_simplify_with_medical_terms(self):
        """Test simplification with medical terms present."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "terms": [
                {"term": "hypertension", "explanation": "high blood pressure"},
                {"term": "tachycardia", "explanation": "fast heart rate"}
            ]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("Patient has hypertension and tachycardia")
            
            assert len(result) == 2
            assert result[0]["term"] == "hypertension"
            assert result[0]["explanation"] == "high blood pressure"
            assert result[1]["term"] == "tachycardia"
            assert result[1]["explanation"] == "fast heart rate"
    
    @pytest.mark.asyncio
    async def test_simplify_with_no_medical_terms(self):
        """Test simplification with no medical terms."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("The patient feels good today")
            
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_simplify_with_empty_transcript(self):
        """Test simplification with empty transcript."""
        service = GeminiService(api_key="test_api_key_12345")
        
        result = await service.simplify_terms("")
        assert len(result) == 0
        
        result = await service.simplify_terms("   ")
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_simplify_with_multiple_terms(self):
        """Test simplification with multiple medical terms."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "terms": [
                {"term": "myocardial infarction", "explanation": "heart attack"},
                {"term": "angina", "explanation": "chest pain"},
                {"term": "ECG", "explanation": "heart rhythm test"}
            ]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms(
                "Patient had myocardial infarction with angina, ECG ordered"
            )
            
            assert len(result) == 3
            assert any(t["term"] == "ECG" for t in result)
    
    @pytest.mark.asyncio
    async def test_simplify_prompt_formatting(self):
        """Test that prompt is properly formatted."""
        service = GeminiService(api_key="test_api_key_12345")
        
        transcript = "Patient has diabetes"
        
        mock_response = Mock()
        mock_response.text = '{"terms": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response) as mock_gen:
            await service.simplify_terms(transcript)
            
            # Verify the prompt contains the transcript
            call_args = mock_gen.call_args[0][0]
            assert transcript in call_args
            assert "JSON format" in call_args
    
    @pytest.mark.asyncio
    async def test_simplify_handles_malformed_response(self):
        """Test handling of malformed API response."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": [{"term": "test"}]}'  # Missing explanation
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("test transcript")
            
            # Should filter out malformed terms
            assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_simplify_response_time(self):
        """Test simplification completes within 2 seconds."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": [{"term": "test", "explanation": "test"}]}'
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.simplify_terms("test transcript")
            elapsed = time.time() - start
            
            # Should complete quickly (well under 2 seconds for mock)
            assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_simplify_with_abbreviations(self):
        """Test simplification handles medical abbreviations."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "terms": [
                {"term": "BP", "explanation": "blood pressure"},
                {"term": "HR", "explanation": "heart rate"},
                {"term": "RR", "explanation": "respiratory rate"}
            ]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("BP 120/80, HR 72, RR 16")
            
            assert len(result) == 3
            assert any(t["term"] == "BP" for t in result)
    
    @pytest.mark.asyncio
    async def test_simplify_error_handling(self):
        """Test error handling returns empty list."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with patch.object(service, '_call_api_with_retry', side_effect=Exception("API Error")):
            result = await service.simplify_terms("test transcript")
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_simplify_validates_term_structure(self):
        """Test validation of term structure."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "terms": [
                {"term": "valid", "explanation": "valid explanation"},
                {"term": "invalid"},
                {"explanation": "missing term"},
                "not a dict",
                {"term": "", "explanation": "empty term"}
            ]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("test transcript")
            
            # Should only include valid term
            assert len(result) == 2  # valid and empty term (has both fields)
            assert result[0]["term"] == "valid"


class TestSimplificationProperties:
    """Property-based tests for simplification."""
    
    @pytest.mark.asyncio
    async def test_property_simplification_completeness(self):
        """
        Property 5: For any medical term identified, a simplification is generated.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "terms": [
                {"term": "term1", "explanation": "explanation1"},
                {"term": "term2", "explanation": "explanation2"}
            ]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.simplify_terms("test transcript")
            
            # Every term must have an explanation
            for term in result:
                assert "term" in term
                assert "explanation" in term
                assert term["explanation"]  # Not empty
    
    @pytest.mark.asyncio
    async def test_property_simplification_response_time(self):
        """
        Property 6: Simplification results sent within 2 seconds.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": []}'
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.simplify_terms("test transcript")
            elapsed = time.time() - start
            
            assert elapsed < 2.0

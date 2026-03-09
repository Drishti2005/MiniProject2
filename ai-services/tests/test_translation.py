"""
Tests for translation functionality.
"""

import pytest
from unittest.mock import Mock, patch
from gemini_service import GeminiService


class TestTranslateText:
    """Test translation functionality."""
    
    @pytest.mark.asyncio
    async def test_translate_to_spanish(self):
        """Test translation to Spanish."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Presión arterial alta"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("High blood pressure", "es")
            
            assert result == "Presión arterial alta"
    
    @pytest.mark.asyncio
    async def test_translate_to_hindi(self):
        """Test translation to Hindi."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "उच्च रक्तचाप"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("High blood pressure", "hi")
            
            assert result == "उच्च रक्तचाप"
    
    @pytest.mark.asyncio
    async def test_translate_to_mandarin(self):
        """Test translation to Mandarin."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "高血压"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("High blood pressure", "zh")
            
            assert result == "高血压"
    
    @pytest.mark.asyncio
    async def test_translate_to_french(self):
        """Test translation to French."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Hypertension artérielle"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("High blood pressure", "fr")
            
            assert result == "Hypertension artérielle"
    
    @pytest.mark.asyncio
    async def test_translate_to_arabic(self):
        """Test translation to Arabic."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "ارتفاع ضغط الدم"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("High blood pressure", "ar")
            
            assert result == "ارتفاع ضغط الدم"
    
    @pytest.mark.asyncio
    async def test_translate_unsupported_language(self):
        """Test translation to unsupported language raises error."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with pytest.raises(ValueError, match="Unsupported language"):
            await service.translate_text("Test", "de")  # German not supported
    
    @pytest.mark.asyncio
    async def test_translate_empty_text(self):
        """Test translation with empty text."""
        service = GeminiService(api_key="test_api_key_12345")
        
        result = await service.translate_text("", "es")
        assert result == ""
        
        result = await service.translate_text("   ", "es")
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_translate_with_medical_terminology(self):
        """Test translation maintains medical accuracy."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Infarto de miocardio"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("Myocardial infarction", "es")
            
            assert result == "Infarto de miocardio"
    
    @pytest.mark.asyncio
    async def test_translate_with_simple_explanation(self):
        """Test translation of simple explanations."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Ataque al corazón"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("Heart attack", "es")
            
            assert result == "Ataque al corazón"
    
    @pytest.mark.asyncio
    async def test_translate_prompt_formatting(self):
        """Test that translation prompt is properly formatted."""
        service = GeminiService(api_key="test_api_key_12345")
        
        text = "High blood pressure"
        
        mock_response = Mock()
        mock_response.text = "Translated text"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response) as mock_gen:
            await service.translate_text(text, "es")
            
            # Verify the prompt contains the text and language
            call_args = mock_gen.call_args[0][0]
            assert text in call_args
            assert "Spanish" in call_args
            assert "patient-friendly" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_translate_response_time(self):
        """Test translation completes within 2 seconds."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Translated text"
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.translate_text("Test text", "es")
            elapsed = time.time() - start
            
            assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_translate_error_handling(self):
        """Test error handling returns original text."""
        service = GeminiService(api_key="test_api_key_12345")
        
        original_text = "Test text"
        
        with patch.object(service, '_call_api_with_retry', side_effect=Exception("API Error")):
            result = await service.translate_text(original_text, "es")
            
            # Should return original text on error
            assert result == original_text
    
    @pytest.mark.asyncio
    async def test_translate_strips_whitespace(self):
        """Test translation strips extra whitespace."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "  Translated text  \n"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("Test", "es")
            
            assert result == "Translated text"
    
    @pytest.mark.asyncio
    async def test_translate_all_supported_languages(self):
        """Test translation works for all supported languages."""
        service = GeminiService(api_key="test_api_key_12345")
        
        supported_languages = ["es", "hi", "zh", "fr", "ar"]
        
        mock_response = Mock()
        mock_response.text = "Translated"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            for lang in supported_languages:
                result = await service.translate_text("Test", lang)
                assert result == "Translated"


class TestTranslationProperties:
    """Property-based tests for translation."""
    
    @pytest.mark.asyncio
    async def test_property_translation_transmission(self):
        """
        Property 28: Translation sent within 2 seconds.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Translated"
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.translate_text("Test", "es")
            elapsed = time.time() - start
            
            assert elapsed < 2.0
    
    @pytest.mark.asyncio
    async def test_property_translation_non_empty(self):
        """Property: Translation of non-empty text returns non-empty result."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = "Translated"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.translate_text("Test", "es")
            
            assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_property_supported_languages(self):
        """Property: All supported languages work without errors."""
        service = GeminiService(api_key="test_api_key_12345")
        
        supported_languages = ["es", "hi", "zh", "fr", "ar"]
        
        mock_response = Mock()
        mock_response.text = "Translated"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            for lang in supported_languages:
                result = await service.translate_text("Test", lang)
                assert isinstance(result, str)

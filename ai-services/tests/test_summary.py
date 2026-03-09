"""
Tests for visit summary generation functionality.
"""

import pytest
from unittest.mock import Mock, patch
from gemini_service import GeminiService


class TestGenerateSummary:
    """Test visit summary generation."""
    
    @pytest.mark.asyncio
    async def test_generate_complete_summary(self):
        """Test generation of complete visit summary."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Hypertension Follow-up",
            "diagnosis": "Essential hypertension, well-controlled",
            "medications": ["Lisinopril 10mg daily", "Aspirin 81mg daily"],
            "instructions": ["Monitor blood pressure daily", "Reduce sodium intake"],
            "follow_up": "Return in 3 months",
            "key_points": ["BP improved", "Continue current medications", "Lifestyle modifications working"]
        }
        '''
        
        transcript = "Doctor discussed blood pressure management with patient..."
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary(transcript)
            
            assert result["title"] == "Hypertension Follow-up"
            assert result["diagnosis"] == "Essential hypertension, well-controlled"
            assert len(result["medications"]) == 2
            assert len(result["instructions"]) == 2
            assert result["follow_up"] == "Return in 3 months"
            assert len(result["key_points"]) == 3
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_short_conversation(self):
        """Test summary generation with short conversation."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Brief Consultation",
            "diagnosis": "General checkup",
            "medications": [],
            "instructions": ["Continue current routine"],
            "follow_up": "As needed",
            "key_points": ["Patient feeling well"]
        }
        '''
        
        transcript = "Quick checkup, patient doing well."
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary(transcript)
            
            assert result["title"] == "Brief Consultation"
            assert len(result["medications"]) == 0
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_empty_transcript(self):
        """Test summary generation with empty transcript."""
        service = GeminiService(api_key="test_api_key_12345")
        
        result = await service.generate_summary("")
        
        assert result["title"] == "Medical Visit"
        assert result["diagnosis"] == ""
        assert result["medications"] == []
        assert result["instructions"] == []
        assert result["follow_up"] == ""
        assert result["key_points"] == []
    
    @pytest.mark.asyncio
    async def test_generate_summary_validates_structure(self):
        """Test summary structure validation."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Test Visit",
            "diagnosis": "Test diagnosis",
            "medications": "Not an array",
            "instructions": ["Valid instruction"],
            "follow_up": "Test follow-up"
        }
        '''
        
        transcript = "Test transcript"
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary(transcript)
            
            # Should normalize invalid fields
            assert result["medications"] == []  # Invalid type converted to empty array
            assert isinstance(result["instructions"], list)
            assert result["key_points"] == []  # Missing field filled with empty array
    
    @pytest.mark.asyncio
    async def test_generate_summary_prompt_formatting(self):
        """Test that summary prompt is properly formatted."""
        service = GeminiService(api_key="test_api_key_12345")
        
        transcript = "Test medical conversation"
        
        mock_response = Mock()
        mock_response.text = '{"title": "Test", "diagnosis": "", "medications": [], "instructions": [], "follow_up": "", "key_points": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response) as mock_gen:
            await service.generate_summary(transcript)
            
            # Verify the prompt contains the transcript
            call_args = mock_gen.call_args[0][0]
            assert transcript in call_args
            assert "structured summary" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_multiple_diagnoses(self):
        """Test summary handles multiple diagnoses."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Multiple Conditions Review",
            "diagnosis": "Hypertension, Type 2 Diabetes, Hyperlipidemia",
            "medications": ["Lisinopril 10mg", "Metformin 500mg", "Atorvastatin 20mg"],
            "instructions": ["Monitor BP", "Check blood sugar", "Low-fat diet"],
            "follow_up": "Return in 1 month",
            "key_points": ["All conditions stable", "Continue medications", "Lab work needed"]
        }
        '''
        
        transcript = "Patient has multiple chronic conditions..."
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary(transcript)
            
            assert "Hypertension" in result["diagnosis"]
            assert "Diabetes" in result["diagnosis"]
            assert len(result["medications"]) == 3
    
    @pytest.mark.asyncio
    async def test_generate_summary_extracts_medication_dosages(self):
        """Test summary extracts medication names and dosages."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Medication Review",
            "diagnosis": "Hypertension",
            "medications": ["Lisinopril 10mg once daily", "Hydrochlorothiazide 25mg once daily"],
            "instructions": ["Take medications with food"],
            "follow_up": "Return in 2 weeks",
            "key_points": ["New medication regimen"]
        }
        '''
        
        transcript = "Prescribing Lisinopril 10mg and Hydrochlorothiazide 25mg..."
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary(transcript)
            
            # Check medications include dosages
            assert any("10mg" in med for med in result["medications"])
            assert any("25mg" in med for med in result["medications"])
    
    @pytest.mark.asyncio
    async def test_generate_summary_response_time(self):
        """Test summary generation completes within 10 seconds."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"title": "Test", "diagnosis": "", "medications": [], "instructions": [], "follow_up": "", "key_points": []}'
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.generate_summary("Test transcript")
            elapsed = time.time() - start
            
            # Should complete quickly (well under 10 seconds for mock)
            assert elapsed < 10.0
    
    @pytest.mark.asyncio
    async def test_generate_summary_error_handling(self):
        """Test error handling returns empty summary."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with patch.object(service, '_call_api_with_retry', side_effect=Exception("API Error")):
            result = await service.generate_summary("Test transcript")
            
            # Should return empty summary structure
            assert result["title"] == "Medical Visit"
            assert result["diagnosis"] == ""
            assert result["medications"] == []
    
    @pytest.mark.asyncio
    async def test_generate_summary_handles_missing_fields(self):
        """Test handling of response with missing fields."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Partial Summary",
            "diagnosis": "Test diagnosis"
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary("Test transcript")
            
            # Should fill missing fields with defaults
            assert result["title"] == "Partial Summary"
            assert result["diagnosis"] == "Test diagnosis"
            assert result["medications"] == []
            assert result["instructions"] == []
            assert result["follow_up"] == ""
            assert result["key_points"] == []


class TestSummaryProperties:
    """Property-based tests for summary generation."""
    
    @pytest.mark.asyncio
    async def test_property_summary_structure_completeness(self):
        """
        Property 21: For any summary generated, all required fields present.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Test",
            "diagnosis": "Test",
            "medications": [],
            "instructions": [],
            "follow_up": "Test",
            "key_points": []
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary("Test transcript")
            
            # All required fields must be present
            required_fields = ["title", "diagnosis", "medications", "instructions", "follow_up", "key_points"]
            for field in required_fields:
                assert field in result
    
    @pytest.mark.asyncio
    async def test_property_summary_array_fields(self):
        """Property: Array fields must be lists."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '''
        {
            "title": "Test",
            "diagnosis": "Test",
            "medications": ["Med1"],
            "instructions": ["Inst1"],
            "follow_up": "Test",
            "key_points": ["Point1"]
        }
        '''
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service.generate_summary("Test transcript")
            
            # Array fields must be lists
            assert isinstance(result["medications"], list)
            assert isinstance(result["instructions"], list)
            assert isinstance(result["key_points"], list)
    
    @pytest.mark.asyncio
    async def test_property_summary_generation_time(self):
        """
        Property 25: Summary generated within 10 seconds.
        """
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"title": "Test", "diagnosis": "", "medications": [], "instructions": [], "follow_up": "", "key_points": []}'
        
        import time
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            start = time.time()
            await service.generate_summary("Test transcript")
            elapsed = time.time() - start
            
            assert elapsed < 10.0

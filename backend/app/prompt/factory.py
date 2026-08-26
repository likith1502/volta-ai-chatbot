import logging

from app.prompt.templates.chat_template import ChatPromptTemplate
from app.prompt.templates.system_template import SystemPromptTemplate

logger = logging.getLogger("app.prompt.factory")


class PromptFactory:
    """Factory creating built-in prompt template presets for VOLTA AI Chatbot."""

    @staticmethod
    def create_mobility_assistant_template() -> SystemPromptTemplate:
        """Creates preset template for VOLTA Urban Mobility Assistant."""
        template = SystemPromptTemplate(
            template_id="mobility_assistant_v1",
            system_instruction="You are VOLTA AI Chatbot, an urban mobility & ride-booking assistant for {city_name}. Help users book rides, check ETAs, and discover popular destinations.",
        )
        template.add_variable(
            name="city_name",
            required=True,
            default_value="San Francisco",
            description="Target city name",
        )
        template.add_variable(
            name="user_name",
            required=False,
            default_value="Traveler",
            description="User's display name",
        )
        template.add_message(
            role="user", content_template="Hello! I need a ride in {city_name}."
        )
        return template

    @staticmethod
    def create_ride_booking_template() -> ChatPromptTemplate:
        """Creates preset template for Ride Booking turn."""
        template = ChatPromptTemplate(
            template_id="ride_booking_v1",
            system_instruction="You are VOLTA Booking Specialist. Calculate ride fare estimates and confirm pickup locations.",
        )
        template.add_variable(
            name="pickup_location", required=True, description="User's pickup location"
        )
        template.add_variable(
            name="dropoff_location",
            required=True,
            description="User's dropoff destination",
        )
        template.add_variable(
            name="vehicle_type",
            required=False,
            default_value="Sedan",
            description="Vehicle category",
        )
        template.add_message(
            role="user",
            content_template="Please book a {vehicle_type} from {pickup_location} to {dropoff_location}.",
        )
        return template

    @staticmethod
    def create_system_chat_template() -> ChatPromptTemplate:
        """Creates generic chat template preset."""
        template = ChatPromptTemplate(
            template_id="system_chat_v1",
            system_instruction="You are a helpful AI assistant for VOLTA platform.",
        )
        template.add_variable(
            name="query", required=True, description="User query text"
        )
        template.add_message(role="user", content_template="{query}")
        return template

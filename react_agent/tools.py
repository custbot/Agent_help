"""This module provides example tools for web scraping, search functionality, and company-specific FAQs.

It includes a basic Tavily search function and an FAQ tool for DCS-specific information.

These tools are intended as examples to get started. For production use, consider implementing more robust and specialized tools.
"""
import re
from sympy import sympify
from langchain_core.tools import Tool
from typing import Any, Callable, List, Optional, cast
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg
from typing_extensions import Annotated
from react_agent.configuration import Configuration

@tool



def calculate(expression: str, decimals: int = 2) -> str:
    """
    Perform basic mathematical calculations and return the result.

    Supports addition, subtraction, multiplication, division, and percentage.

    Args:
        expression: A string representing the mathematical expression.
        decimals: Number of decimal places for the result.
    Example:
        calculate("2 + 3 * 5") -> "17.00"
        calculate("20% of 150") -> "30.00"
    """
    try:
        # Handle percentages: Convert "20% of 150" to "20/100 * 150"
        expression = re.sub(r'(\d+)% of (\d+)', r'(\1/100) * \2', expression)

        # Convert the expression into a symbolic format and evaluate
        result = sympify(expression).evalf()

        # Format the result with the specified number of decimal places
        return f"{float(result):.{decimals}f}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


# Sample data for demonstration purposes
invoice_data = {
    "12345": {"total_amount": 1000.0, "status": "Paid", "date": "2024-01-10"},
    "67890": {"total_amount": 250.0, "status": "Pending", "date": "2024-02-20"},
    "54321": {"total_amount": 150.0, "status": "Overdue", "date": "2023-12-05"},
}

def lookup_invoice(customer_id: str) -> str:
    """Fetches invoice information for a given customer ID."""
    invoice = invoice_data.get(customer_id)
    if invoice:
        return (
            f"Invoice for customer {customer_id}: Total Amount: #{invoice['total_amount']}, "
            f"Status: {invoice['status']}, Date: {invoice['date']}."
        )
    else:
        return f"No invoice found for customer ID {customer_id}."






# Define the search tool
async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)

# Register all tools in the TOOLS list

TOOLS : List[Callable[..., Any]] = [search, calculate, lookup_invoice ]
# llm_with_tools = llm.bind_tools(TOOLS)
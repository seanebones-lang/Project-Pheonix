"""
Math solver utilities using SymPy.
"""

from typing import Dict, Any, List, Optional, Union
from sympy import symbols, sympify, solve, simplify, latex, pretty_print
from sympy.parsing.sympy_parser import parse_expr
from sympy.calculus import diff, integrate
from sympy.solvers import solve_linear_system
from sympy.matrices import Matrix
import re

class MathSolver:
    """Utility class for mathematical problem solving."""
    
    @staticmethod
    def solve_linear_equation(equation: str) -> Dict[str, Any]:
        """Solve a linear equation."""
        try:
            left, right = equation.split('=')
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            
            eq = left_expr - right_expr
            variables = list(eq.free_symbols)
            
            if not variables:
                return {'error': 'No variables found in equation'}
            
            solutions = solve(eq, variables[0])
            
            return {
                'solutions': solutions,
                'latex': f"${latex(solutions[0])}$" if solutions else None,
                'steps': [
                    f"Given: {equation}",
                    f"Rearrange: {left_expr} = {right_expr}",
                    f"Solve: {variables[0]} = {solutions[0] if solutions else 'No solution'}"
                ]
            }
            
        except Exception as e:
            return {'error': f'Error solving linear equation: {str(e)}'}
    
    @staticmethod
    def solve_quadratic_equation(equation: str) -> Dict[str, Any]:
        """Solve a quadratic equation."""
        try:
            left, right = equation.split('=')
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            
            eq = left_expr - right_expr
            variables = list(eq.free_symbols)
            
            if not variables:
                return {'error': 'No variables found in equation'}
            
            solutions = solve(eq, variables[0])
            
            return {
                'solutions': solutions,
                'latex': f"${latex(solutions)}$" if solutions else None,
                'discriminant': eq.discriminant() if hasattr(eq, 'discriminant') else None
            }
            
        except Exception as e:
            return {'error': f'Error solving quadratic equation: {str(e)}'}
    
    @staticmethod
    def calculate_derivative(function: str, variable: str = 'x') -> Dict[str, Any]:
        """Calculate derivative of a function."""
        try:
            expr = parse_expr(function)
            var = symbols(variable)
            derivative = diff(expr, var)
            
            return {
                'function': str(expr),
                'derivative': str(simplify(derivative)),
                'latex': f"$\\frac{{d}}{{d{variable}}}({latex(expr)}) = {latex(simplify(derivative))}$"
            }
            
        except Exception as e:
            return {'error': f'Error calculating derivative: {str(e)}'}
    
    @staticmethod
    def calculate_integral(function: str, variable: str = 'x') -> Dict[str, Any]:
        """Calculate integral of a function."""
        try:
            expr = parse_expr(function)
            var = symbols(variable)
            integral = integrate(expr, var)
            
            return {
                'function': str(expr),
                'integral': str(simplify(integral)),
                'latex': f"$\\int {latex(expr)} \\, d{variable} = {latex(simplify(integral))}$"
            }
            
        except Exception as e:
            return {'error': f'Error calculating integral: {str(e)}'}
    
    @staticmethod
    def simplify_expression(expression: str) -> Dict[str, Any]:
        """Simplify a mathematical expression."""
        try:
            expr = parse_expr(expression)
            simplified = simplify(expr)
            
            return {
                'original': str(expr),
                'simplified': str(simplified),
                'latex': f"${latex(simplified)}$"
            }
            
        except Exception as e:
            return {'error': f'Error simplifying expression: {str(e)}'}
    
    @staticmethod
    def solve_system_of_equations(equations: List[str]) -> Dict[str, Any]:
        """Solve a system of linear equations."""
        try:
            # Parse equations
            parsed_eqs = []
            variables = set()
            
            for eq in equations:
                left, right = eq.split('=')
                left_expr = parse_expr(left.strip())
                right_expr = parse_expr(right.strip())
                parsed_eqs.append(left_expr - right_expr)
                variables.update(left_expr.free_symbols)
                variables.update(right_expr.free_symbols)
            
            variables = list(variables)
            
            if len(variables) != len(parsed_eqs):
                return {'error': 'Number of variables must equal number of equations'}
            
            # Solve system
            solutions = solve(parsed_eqs, variables)
            
            return {
                'equations': equations,
                'variables': [str(v) for v in variables],
                'solutions': solutions,
                'latex': f"${latex(solutions)}$" if solutions else None
            }
            
        except Exception as e:
            return {'error': f'Error solving system of equations: {str(e)}'}
    
    @staticmethod
    def extract_equation_from_text(text: str) -> Optional[str]:
        """Extract mathematical equation from text."""
        patterns = [
            r'solve\s+(.+)',           # "solve x + 2 = 5"
            r'(.+=\d+)',               # "x + 2 = 5"
            r'(.+=\w+)',               # "x + 2 = y"
            r'calculate\s+(.+)',       # "calculate x^2 + 3x"
            r'evaluate\s+(.+)',        # "evaluate 2x + 1"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def detect_math_operation(text: str) -> str:
        """Detect the type of mathematical operation from text."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['solve', 'find', 'calculate']):
            if '=' in text:
                return 'equation'
            else:
                return 'expression'
        elif any(keyword in text_lower for keyword in ['derivative', 'differentiate']):
            return 'derivative'
        elif any(keyword in text_lower for keyword in ['integral', 'integrate']):
            return 'integral'
        elif any(keyword in text_lower for keyword in ['simplify', 'expand']):
            return 'simplify'
        else:
            return 'unknown'
    
    @staticmethod
    def format_solution(solution: Any, format_type: str = 'latex') -> str:
        """Format solution in different formats."""
        try:
            if format_type == 'latex':
                return f"${latex(solution)}$"
            elif format_type == 'pretty':
                return str(pretty_print(solution, use_unicode=True))
            elif format_type == 'text':
                return str(solution)
            else:
                return str(solution)
        except Exception as e:
            return f"Error formatting solution: {str(e)}"

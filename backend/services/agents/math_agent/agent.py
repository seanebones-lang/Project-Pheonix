"""
Math Agent implementation using SymPy for mathematical problem solving.
"""

import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from sympy import symbols, sympify, solve, simplify, latex, pretty_print
from sympy.parsing.sympy_parser import parse_expr
from sympy.calculus import diff, integrate
from sympy.solvers import solve_linear_system
from sympy.matrices import Matrix

from ..base.agent_base import BaseAgent
from ...shared.models import Task, TaskStatus

class MathAgent(BaseAgent):
    """Specialized agent for mathematical problem solving."""
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or str(uuid.uuid4()),
            agent_name="Math Solver",
            agent_type="math",
            capabilities={
                "algebra": ["linear_equations", "quadratic_equations", "polynomials"],
                "calculus": ["derivatives", "integrals", "limits"],
                "trigonometry": ["sin", "cos", "tan", "inverse_trig"],
                "statistics": ["mean", "median", "mode", "standard_deviation"],
                "geometry": ["area", "perimeter", "volume", "angles"],
                "output_formats": ["step_by_step", "final_answer", "latex", "pretty_print"]
            }
        )
    
    def _can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle mathematical tasks."""
        input_data = task.input_data
        
        # Check if input contains mathematical expressions
        if isinstance(input_data, dict):
            problem = input_data.get('problem', '') or input_data.get('equation', '') or str(input_data)
        else:
            problem = str(input_data)
        
        # Simple heuristic to detect math problems
        math_indicators = [
            r'[+\-*/=]',  # Basic operators
            r'\d+',       # Numbers
            r'[a-zA-Z]',  # Variables
            r'[()]',      # Parentheses
            r'solve|calculate|find|compute',  # Math keywords
            r'equation|formula|function'       # Math terms
        ]
        
        return any(re.search(pattern, problem.lower()) for pattern in math_indicators)
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute mathematical problem solving task."""
        input_data = task.input_data
        
        try:
            # Extract problem information
            problem = input_data.get('problem', '') or input_data.get('equation', '') or str(input_data)
            problem_type = input_data.get('type', 'auto_detect')
            output_format = input_data.get('output_format', 'step_by_step')
            
            # Detect problem type if not specified
            if problem_type == 'auto_detect':
                problem_type = self._detect_problem_type(problem)
            
            # Solve the problem
            solution = await self._solve_problem(problem, problem_type, output_format)
            
            return {
                'problem': problem,
                'problem_type': problem_type,
                'solution': solution,
                'output_format': output_format,
                'solved_at': datetime.utcnow().isoformat(),
                'agent_name': self.agent_name
            }
            
        except Exception as e:
            raise Exception(f"Math solving error: {str(e)}")
    
    def _detect_problem_type(self, problem: str) -> str:
        """Detect the type of mathematical problem."""
        problem_lower = problem.lower()
        
        # Calculus
        if any(keyword in problem_lower for keyword in ['derivative', 'differentiate', 'd/dx', 'integral', 'integrate']):
            return 'calculus'
        
        # Linear equations
        if '=' in problem and not any(op in problem for op in ['^', '**', 'sqrt']):
            return 'linear_equation'
        
        # Quadratic equations
        if any(keyword in problem_lower for keyword in ['quadratic', 'x^2', 'x**2']):
            return 'quadratic_equation'
        
        # Trigonometry
        if any(func in problem_lower for func in ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh']):
            return 'trigonometry'
        
        # Polynomial
        if any(op in problem for op in ['^', '**']) and '=' in problem:
            return 'polynomial'
        
        # Default to algebra
        return 'algebra'
    
    async def _solve_problem(self, problem: str, problem_type: str, output_format: str) -> Dict[str, Any]:
        """Solve the mathematical problem based on type."""
        
        if problem_type == 'linear_equation':
            return await self._solve_linear_equation(problem, output_format)
        elif problem_type == 'quadratic_equation':
            return await self._solve_quadratic_equation(problem, output_format)
        elif problem_type == 'polynomial':
            return await self._solve_polynomial(problem, output_format)
        elif problem_type == 'calculus':
            return await self._solve_calculus(problem, output_format)
        elif problem_type == 'trigonometry':
            return await self._solve_trigonometry(problem, output_format)
        else:
            return await self._solve_general(problem, output_format)
    
    async def _solve_linear_equation(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve linear equations."""
        try:
            # Extract equation from problem
            equation = self._extract_equation(problem)
            
            # Parse equation
            left, right = equation.split('=')
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            
            # Create equation
            eq = left_expr - right_expr
            
            # Find variables
            variables = list(eq.free_symbols)
            if not variables:
                return {'error': 'No variables found in equation'}
            
            # Solve equation
            solutions = solve(eq, variables[0])
            
            if output_format == 'step_by_step':
                steps = [
                    f"Given equation: {equation}",
                    f"Rearrange: {left_expr} = {right_expr}",
                    f"Simplify: {eq} = 0",
                    f"Solve for {variables[0]}: {variables[0]} = {solutions[0] if solutions else 'No solution'}"
                ]
                
                return {
                    'steps': steps,
                    'final_answer': solutions[0] if solutions else None,
                    'latex': f"${latex(solutions[0])}$" if solutions else None
                }
            else:
                return {
                    'final_answer': solutions[0] if solutions else None,
                    'latex': f"${latex(solutions[0])}$" if solutions else None
                }
                
        except Exception as e:
            return {'error': f'Error solving linear equation: {str(e)}'}
    
    async def _solve_quadratic_equation(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve quadratic equations."""
        try:
            equation = self._extract_equation(problem)
            left, right = equation.split('=')
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            
            eq = left_expr - right_expr
            variables = list(eq.free_symbols)
            
            if not variables:
                return {'error': 'No variables found in equation'}
            
            solutions = solve(eq, variables[0])
            
            if output_format == 'step_by_step':
                steps = [
                    f"Given equation: {equation}",
                    f"Rearrange: {left_expr} = {right_expr}",
                    f"Simplify: {eq} = 0",
                    f"Solve for {variables[0]}:"
                ]
                
                for i, sol in enumerate(solutions):
                    steps.append(f"  Solution {i+1}: {variables[0]} = {sol}")
                
                return {
                    'steps': steps,
                    'solutions': solutions,
                    'latex': f"${latex(solutions)}$" if solutions else None
                }
            else:
                return {
                    'solutions': solutions,
                    'latex': f"${latex(solutions)}$" if solutions else None
                }
                
        except Exception as e:
            return {'error': f'Error solving quadratic equation: {str(e)}'}
    
    async def _solve_polynomial(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve polynomial equations."""
        try:
            equation = self._extract_equation(problem)
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
                'degree': eq.degree(variables[0]) if variables else 0
            }
            
        except Exception as e:
            return {'error': f'Error solving polynomial: {str(e)}'}
    
    async def _solve_calculus(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve calculus problems."""
        try:
            problem_lower = problem.lower()
            
            if 'derivative' in problem_lower or 'differentiate' in problem_lower:
                return await self._solve_derivative(problem, output_format)
            elif 'integral' in problem_lower or 'integrate' in problem_lower:
                return await self._solve_integral(problem, output_format)
            else:
                return {'error': 'Unsupported calculus operation'}
                
        except Exception as e:
            return {'error': f'Error solving calculus problem: {str(e)}'}
    
    async def _solve_derivative(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve derivative problems."""
        try:
            # Extract function from problem
            func_expr = self._extract_function(problem)
            expr = parse_expr(func_expr)
            
            # Find variable
            variables = list(expr.free_symbols)
            if not variables:
                return {'error': 'No variables found in function'}
            
            # Calculate derivative
            derivative = diff(expr, variables[0])
            
            if output_format == 'step_by_step':
                steps = [
                    f"Given function: f(x) = {expr}",
                    f"Find derivative: f'(x) = {derivative}",
                    f"Simplified: f'(x) = {simplify(derivative)}"
                ]
                
                return {
                    'steps': steps,
                    'derivative': str(simplify(derivative)),
                    'latex': f"$\\frac{{d}}{{dx}}({latex(expr)}) = {latex(simplify(derivative))}$"
                }
            else:
                return {
                    'derivative': str(simplify(derivative)),
                    'latex': f"$\\frac{{d}}{{dx}}({latex(expr)}) = {latex(simplify(derivative))}$"
                }
                
        except Exception as e:
            return {'error': f'Error calculating derivative: {str(e)}'}
    
    async def _solve_integral(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve integral problems."""
        try:
            func_expr = self._extract_function(problem)
            expr = parse_expr(func_expr)
            
            variables = list(expr.free_symbols)
            if not variables:
                return {'error': 'No variables found in function'}
            
            # Calculate integral
            integral = integrate(expr, variables[0])
            
            if output_format == 'step_by_step':
                steps = [
                    f"Given function: f(x) = {expr}",
                    f"Find integral: ∫f(x)dx = {integral}",
                    f"Simplified: ∫f(x)dx = {simplify(integral)}"
                ]
                
                return {
                    'steps': steps,
                    'integral': str(simplify(integral)),
                    'latex': f"$\\int {latex(expr)} \\, dx = {latex(simplify(integral))}$"
                }
            else:
                return {
                    'integral': str(simplify(integral)),
                    'latex': f"$\\int {latex(expr)} \\, dx = {latex(simplify(integral))}$"
                }
                
        except Exception as e:
            return {'error': f'Error calculating integral: {str(e)}'}
    
    async def _solve_trigonometry(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve trigonometry problems."""
        try:
            equation = self._extract_equation(problem)
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
                'latex': f"${latex(solutions)}$" if solutions else None
            }
            
        except Exception as e:
            return {'error': f'Error solving trigonometry problem: {str(e)}'}
    
    async def _solve_general(self, problem: str, output_format: str) -> Dict[str, Any]:
        """Solve general mathematical problems."""
        try:
            # Try to parse as expression
            expr = parse_expr(problem)
            
            # Simplify if possible
            simplified = simplify(expr)
            
            return {
                'expression': str(expr),
                'simplified': str(simplified),
                'latex': f"${latex(simplified)}$"
            }
            
        except Exception as e:
            return {'error': f'Error solving general problem: {str(e)}'}
    
    def _extract_equation(self, problem: str) -> str:
        """Extract equation from problem text."""
        # Look for patterns like "solve x + 2 = 5" or "x + 2 = 5"
        patterns = [
            r'solve\s+(.+)',  # "solve x + 2 = 5"
            r'(.+=\d+)',      # "x + 2 = 5"
            r'(.+=\w+)',      # "x + 2 = y"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, problem, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the original problem
        return problem
    
    def _extract_function(self, problem: str) -> str:
        """Extract function from problem text."""
        # Look for patterns like "f(x) = x^2" or "differentiate x^2"
        patterns = [
            r'f\([^)]+\)\s*=\s*(.+)',  # "f(x) = x^2"
            r'differentiate\s+(.+)',   # "differentiate x^2"
            r'integrate\s+(.+)',        # "integrate x^2"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, problem, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, return the original problem
        return problem

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = MathAgent()
        await agent.start()
    
    asyncio.run(main())

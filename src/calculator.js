/**
 * Simple Calculator Function
 * Performs basic arithmetic operations: addition, subtraction, multiplication, and division
 */

// Main calculator function
function calculator(operation, a, b) {
  // Convert inputs to numbers to ensure proper calculation
  a = Number(a);
  b = Number(b);
  
  // Check if inputs are valid numbers
  if (isNaN(a) || isNaN(b)) {
    return "Error: Inputs must be valid numbers";
  }
  
  // Perform the requested operation
  switch (operation.toLowerCase()) {
    case "add":
    case "+":
      return a + b;
      
    case "subtract":
    case "-":
      return a - b;
      
    case "multiply":
    case "*":
      return a * b;
      
    case "divide":
    case "/":
      // Check for division by zero
      if (b === 0) {
        return "Error: Division by zero is not allowed";
      }
      return a / b;
      
    default:
      return "Error: Invalid operation. Supported operations are: add(+), subtract(-), multiply(*), divide(/)";
  }
}

// Example usage
console.log("Calculator Examples:");
console.log("Addition: 5 + 3 =", calculator("add", 5, 3));
console.log("Subtraction: 10 - 4 =", calculator("-", 10, 4));
console.log("Multiplication: 6 * 7 =", calculator("*", 6, 7));
console.log("Division: 20 / 5 =", calculator("divide", 20, 5));
console.log("Division by zero:", calculator("/", 10, 0));
console.log("Invalid input:", calculator("+", "abc", 5));

// Export the calculator function for use in other modules
module.exports = calculator;
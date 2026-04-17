function parseUserInput(userInput) {
  const { product, keyPoints, useCase } = userInput;
  
  return {
    product: product.trim(),
    keyPoints: keyPoints.split(',').map(point => point.trim()).filter(point => point),
    useCase: useCase.trim()
  };
}

module.exports = { parseUserInput };
> Generated with AI Article Generator
>
> **Metadata**
> - Requested model: google/gemma-3-12b-it:free
> - Model used: google/gemma-3-12b-it:free
> - Total generate time: 2m 3s
> - Total words: 971
> - API calls: 7
> - Successful calls: 7
> - Failed calls: 0
> - Rate limit hits: 0
> - Prompt tokens: 1570
> - Completion tokens: 0
> - Total tokens: 1570
> 

# Logistic regression, One neuron opening towards complexity

## The Basics

## The Basics

Logistic regression, despite its name, is a classification algorithm. It's used to predict the probability of a binary outcome – something that can be either yes or no, true or false, 0 or 1. Think of it like predicting whether an email is spam (1) or not spam (0), or whether a customer will click on an ad (1) or not (0).

At its core, logistic regression uses a linear combination of input features. These features could be anything relevant to the prediction, like email keywords or customer demographics. This linear combination is then passed through a sigmoid function. The sigmoid function, represented as:

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

transforms any real number $z$ into a value between 0 and 1. This output is interpreted as the probability of the outcome being 1.  A value closer to 1 suggests a higher probability of the outcome being true, while a value closer to 0 suggests the opposite.

## Sigmoid Function

## Sigmoid Function

The sigmoid function is crucial to logistic regression. It takes any real-valued input and squashes it into a range between 0 and 1. Think of it as a way to transform the output of our neuron into a probability. 

Mathematically, the sigmoid function is represented as:

$$
\sigma(z) = \frac{1}{1 + e^{-z}}
$$

Here, $z$ represents the input to the sigmoid function (which is the weighted sum of inputs from the previous layer plus a bias), and $e$ is Euler's number (approximately 2.71828).  As $z$ becomes very large, $\sigma(z)$ approaches 1. Conversely, as $z$ becomes very small (a large negative number), $\sigma(z)$ approaches 0. This smooth, S-shaped curve allows us to interpret the neuron's output as the probability of belonging to a certain class. For example, a value close to 1 might indicate a high probability of "yes," while a value close to 0 suggests a high probability of "no."

## Decision Boundary

## Decision Boundary

The decision boundary is a crucial concept in logistic regression. It visually represents where the model separates the different classes. Think of it as a line (in 2D) or a surface (in 3D or higher) that divides the feature space. Points on one side of the boundary are predicted as belonging to one class, while points on the other side are predicted as belonging to the other.

In its simplest form, with a single feature, the decision boundary is a straight line.  The equation for this line is determined by the logistic regression model.  For example, if we have a feature $x$, the decision boundary occurs when the predicted probability, $p$, equals 0.5.  This is where the model is equally likely to predict either class.  As we add more features and the model becomes more complex, the decision boundary can become curved or non-linear, allowing it to capture more intricate patterns in the data.

## Cost Function

**Cost Function**

To train our logistic regression model, we need a way to measure how well it's performing. This is where the cost function comes in. It quantifies the difference between the model's predictions and the actual outcomes.  Essentially, it tells us "how wrong" our model is.

The most common cost function for logistic regression is the *log loss* (also known as cross-entropy loss).  It's designed to penalize incorrect predictions more heavily than slightly incorrect ones.  The formula looks like this:

$$
J = -\frac{1}{m} \sum_{i=1}^{m} [y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i)]
$$

Where:

*   $J$ is the cost.
*   $m$ is the number of training examples.
*   $y_i$ is the actual label (0 or 1) for the $i$-th example.
*   $\hat{y}_i$ is the predicted probability from the model for the $i$-th example.

Our goal during training is to minimize this cost function, meaning we want to find the parameters that make our predictions as close to the true labels as possible.

## Gradient Descent

**Gradient Descent**

Once we have a loss function, we need a way to minimize it. This is where gradient descent comes in. Think of the loss function as a landscape, and our goal is to find the lowest point. Gradient descent is like rolling a ball down that landscape – it iteratively moves towards the minimum.

Mathematically, we adjust the weights ($w$) and bias ($b$) of our logistic regression model. The gradient, denoted by $\nabla L$, points in the direction of the steepest *increase* of the loss function. Therefore, we move in the *opposite* direction, proportional to the learning rate ($\eta$). The update rule looks like this:

$$
w := w - \eta \frac{\partial L}{\partial w}
$$

$$
b := b - \eta \frac{\partial L}{\partial b}
$$

Here, $\eta$ controls the step size. A small learning rate means slow but potentially more accurate convergence, while a large learning rate can overshoot the minimum.

## Beyond Binary Classification

Beyond Binary Classification

While logistic regression shines in binary classification – predicting one of two outcomes – its power extends far beyond that. We can adapt it for multi-class classification problems. Instead of a single sigmoid function, we use a softmax function. This function transforms the output of our single neuron into a probability distribution across multiple classes.

For example, imagine classifying images of animals into categories like "cat," "dog," or "bird." The softmax function ensures that the neuron's output represents the probability of the image belonging to each of these classes, and these probabilities sum to 1.  

Mathematically, the softmax function for $k$ classes is:

$$
P(y=i | x) = \frac{e^{z_i}}{\sum_{j=1}^{k} e^{z_j}}
$$

Where:
* $P(y=i | x)$ is the probability of the input $x$ belonging to class $i$.
* $z_i$ is the output of the neuron for class $i$.
* $k$ is the total number of classes.


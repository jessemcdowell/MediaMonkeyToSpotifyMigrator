import unittest
import Matching

class TestBestMatch(unittest.TestCase):
    def test_returns_none_if_score_less_than_threshold(self):
        first_value = 'hello'
        values = [first_value]
        score = 10
        minimum_score = score + 1
        matchers = [Matching.boolean_matcher(lambda i: i == first_value, score)]

        actual = Matching.best_match(values, matchers, minimum_score)

        self.assertIsNone(actual)

    def test_returns_first_if_score_equals_threshold(self):
        first_value = 'hello'
        values = [first_value]
        minimum_score = score = 10
        matchers = [Matching.boolean_matcher(lambda i: i == first_value, score)]

        actual = Matching.best_match(values, matchers, minimum_score)

        self.assertIs(actual, first_value)

    def test_returns_none_if_rule_does_not_match(self):
        values = ['one']
        minimum_score = score = 10
        matchers = [Matching.boolean_matcher(lambda i: False, score)]

        actual = Matching.best_match(values, matchers, minimum_score)

        self.assertIsNone(actual)

    def test_returns_match_with_highest_score(self):
        second_value = 'two'
        values = ['one', second_value]
        minimum_score = score = 10
        matchers = [
            Matching.boolean_matcher(lambda i: True, score),
            Matching.boolean_matcher(lambda i: i == second_value, score)
        ]

        actual = Matching.best_match(values, matchers, minimum_score)

        self.assertIs(actual, second_value)

    def test_returns_first_match_if_two_have_equal_scores(self):
        second_value = 'two'
        third_value = 'three'
        values = ['one', second_value, third_value]
        minimum_score = score = 10
        matchers = [
            Matching.boolean_matcher(lambda i: True, score),
            Matching.boolean_matcher(lambda i: i == second_value, score),
            Matching.boolean_matcher(lambda i: i == third_value, score)
        ]

        actual = Matching.best_match(values, matchers, minimum_score)

        self.assertIs(actual, second_value)

class TestBooleanMatcher(unittest.TestCase):
    def test_predicate_that_returns_true_returns_score(self):
        score = 10
        matcher = Matching.boolean_matcher(lambda i: True, score)
        actual = matcher('hello')

        self.assertEqual(actual, score)

    def test_predicate_that_returns_false_returns_zero(self):
        matcher = Matching.boolean_matcher(lambda i: False, 10)
        actual = matcher('hello')

        self.assertEqual(actual, 0)

class TestTextMatcher(unittest.TestCase):
    def _match_quality_from_best_to_worst(self, source, compared_to_from_best_to_worst):
        total_possible_score = 1000;

        results = ((Matching.text_matcher(lambda input: input, source, total_possible_score)(compare_to), compare_to) for compare_to in compared_to_from_best_to_worst)
        sorted_results = sorted(results, key=lambda item: item[0], reverse=True)

        self.assertListEqual([item[1] for item in sorted_results], compared_to_from_best_to_worst)

        last_result = None
        for result in sorted_results:
            if last_result:
                self.assertGreater(last_result[0], result[0],
                    f'Score of "{last_result[1]}" ({last_result[0]}) is not greater than "{result[1]}" ({result[0]})')
            last_result = result

    def test_matching_prefers_perfect_then_left_then_right_then_center(self):
        self._match_quality_from_best_to_worst('hello', ['hello', 'hello world', 'oh hello', 'oh hello world', 'potato'])

    def test_match_prefers_substring_from_front_over_substring_from_end(self):
        self._match_quality_from_best_to_worst('hello there', ['hello', 'there', 'potato'])

    def test_match_accept_substring_of_source(self):
        self._match_quality_from_best_to_worst('The Swinging Count!', [
            'The Swinging Count!',
            'The Swinging Count',
            'The Swinging',
            'Swinging',
            'potato'])

    def test_same_word_returns_perfect_score(self):
        compare_to = source = 'hello'
        score = 100

        actual = Matching.text_matcher(lambda input: input, source, score)(compare_to)

        self.assertEqual(actual, score)

    def test_match_prefers_correct_case_over_incorrect_case(self):
        self._match_quality_from_best_to_worst('hello', ['hello', 'Hello', 'potato'])

    def test_same_word_with_different_case_return_same_score(self):
        source = 'hello'
        compare_to = ['Hello', 'HELLO', 'hElLo', 'hellO']

        matcher = Matching.text_matcher(lambda input: input, source, 100)
        actual = [matcher(item) for item in compare_to]

        for i in range(1, len(actual)):
            self.assertEqual(actual[0], actual[i], f'{compare_to[0]} and {compare_to[i]}')

    def test_different_words_return_zero(self):
        actual = Matching.text_matcher(lambda input: input, 'hello', 100)('potato')

        self.assertEqual(actual, 0)

    def test_matching_uses_selected_property(self):
        source = 'hello'
        compare_to = { 'greeting': source, 'response': 'good morning' }
        score = 100

        actual = Matching.text_matcher(lambda input: input['greeting'], source, score)(compare_to)

        self.assertEqual(actual, score)

if __name__ == '__main__':
    unittest.main()

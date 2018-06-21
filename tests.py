import unittest
import sys
from pixel_validator import readFile

file = 'tactic_sample.csv'
tactic_pixels = "[{334448: ['http:\/\/a.bbc/']}, {334448: ['https:\/\/servedby.flashtalking.com\/imp\/4\/46838;1179814;201;pixel;ClearTrade;ClearTradeNativeTabletBlog4SpringLooks1x1\/?cachebuster=[CACHEBUSTER]']}, {337773: ['https:\/\/match.rundsp.com\/witness\/impression.gif?p=94274&a=65568']}]"
num_pixels = 10


class TestPixelValidator(unittest.TestCase):

    def testReadFile(self):
        self.assertEqual(readFile(file)[0], tactic_pixels)

    def testReadFile(self):
        self.assertEqual(readFile(file)[1], num_pixels)


if __name__ == '__main__':
    unittest.main()

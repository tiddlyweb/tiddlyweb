
class ChallengerInterface(object):
    """
    An interface for challenge users for login
    purposes. The chalenger basically does whatever
    it want and _may_ result in doing some to 
    a response that causes the user's next request
    to pass an extractor.

    Though there is no requirement for there to be
    a one to one correspondence between a Challenger
    and an Extractor, it will often be the case
    that a Challenger will need a particular Extractor
    in order to be effective.

    A Challenger needs to take a WSGI request through
    to completion.
    """

    def challenge(self, environ, start_response):
        pass

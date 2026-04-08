'''
Test 1 — confirm under the limit
create merchant
create several payment intents
confirm a few of them
all should succeed until the limit is reached
Test 2 — confirm over the limit
create enough payment intents
confirm more than 5 within 60 seconds
the extra confirm request should return 429
Test 3 — confirm replay should not burn the limit
confirm one payment intent with an idempotency key
repeat the exact same confirm request with the same key multiple times
it should replay the saved response
those replays should not consume additional rate-limit slots
Test 4 — different merchants should not affect each other
merchant A hits the limit
merchant B should still be able to confirm payments normally
'''
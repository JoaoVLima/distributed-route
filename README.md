# distributed-route
A distributed route is used to manage and process messages(AMQP) across different components in a distributed architecture. Using python and pika(rabbitmq).

![image](https://github.com/JoaoVLima/distributed-route/assets/50122442/007ab37b-fca3-44e4-802c-7d1838981f43)

```
States = { INITIATOR, IDLE, VISITED, OK }
    SINI = { INITIATOR, IDLE }
    STERM = { OK }
Constraints: { CN, TR, BL, UI }

INITIATOR
Spontaneously
    not_visited = N(x)
    initiator = true
    visit()

IDLE
Receiving (T) from source
    entry = source
    not_visited = N(x) - { source }
    initiator = false
    visit()

VISITED
Receiving (T) from source
    not_visited = not_visited - { source }
    send (B) to { source }

Receiving (R)
    visit()

Receiving (B)
    visit()

procedure visit()
    if not_visited ≠ ∅:
        not_visited >> next
        state = VISITED
        send (T) to { next }
    else:
        state = OK
        if not initiator:
            send (R) to { entry }
        endif
    endif
```

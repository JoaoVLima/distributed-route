# distributed-route
A distributed route is used to manage and process messages(AMQP) across different components in a distributed architecture. Using Python and pika(RabbitMQ).

![image](https://github.com/JoaoVLima/distributed-route/assets/50122442/007ab37b-fca3-44e4-802c-7d1838981f43)

```
States = { STARTER, IDLE, VISITED, OK }
    SINI = { STARTER, IDLE }
    STERM = { OK }
Constraints: { CN, TR, BL, UI }

STARTER
Spontaneously
    not_visited = N(x)
    starter = true
    visit()

IDLE
Receiving (T) from source
    entry = source
    not_visited = N(x) - { source }
    starter = false
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
        if not starter:
            send (R) to { entry }
        endif
    endif
```

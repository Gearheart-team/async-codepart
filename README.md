This is service for async communication between angular2 and django-channels in wamp-like-protocol.
We can subscribe and publish to async endpoints and call RPC endpionts.

###How to use

Python publish:

```py
from async.methods import publish

publish('com.example.foo', 'some message')
```

See python RPC endpoints example in example/somepymod/rpcendpoints.py

Angular:

```ts
import { Component, Input } from '@angular/core';
import { WampService, RpcCallObservable } from './wamp.service';


@Component({
  selector: 'some-component',
  templateUrl: './some-component.component.html',
  styleUrls: ['./some-component.component.scss']
})
export class SomeComponent {
  @Input() modelId: number;
  heavyMethodResult: any;

  constructor(private wamp: WampService) {
  }

  callRPC() {
    let callObs: RpcCallObservable<any> = this.wamp.call(
      'com.example.heavy',
      [], {model_id: this.modelId})
    callObs.progress.subscribe((msg) => alert(msg));
    callObs.result.subscribe((result) => this.heavyMethodResult = result);
  }

  wampSubscribe() {
    this.wamp.subscribe('com.example.foo', (msg) => alert(msg))
  }

  wampPublish() {
    this.wamp.publish('com.example.foo', 'Foo message')
  }

}```
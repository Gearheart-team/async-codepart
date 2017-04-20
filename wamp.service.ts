import { Injectable } from '@angular/core';

import { Observable, Observer, Subscription, Subject } from 'rxjs/Rx';
import { WebSocketSubject, WebSocketSubjectConfig } from 'rxjs/observable/dom/WebSocketSubject';
import * as uuid from 'uuid';

import { AuthResource } from '../resources/auth.resource';
import { environment } from '../../environments/environment';

export class RpcCallObservable<T> {
  private _resultSubject: Subject<T> = new Subject<T>();
  private _processSubject: Subject<any> = new Subject<any>();
  private _subscription: Subscription;

  public callee_uuid: string;
  public trackingState: boolean = true;

  constructor(private wsSubject: WebSocketSubject<any>, callee_uuid: string) {
    this.callee_uuid = callee_uuid;
    this._subscription = wsSubject
      .filter((msg) => msg.endpoint === callee_uuid)
      .subscribe((message) => {
        if (message.complete) {
          this._resultSubject.next(message.message);
          this.deactivate();
        } else {
          this._processSubject.next(message.message)
        }
      })
  }

  public deactivate() {
      this._resultSubject.complete();
      this._processSubject.complete();
      this._subscription.unsubscribe();
      this.wsSubject.next(JSON.stringify({action: 'unsubscribe', endpoint: this.callee_uuid}));
      this.trackingState = false;
  }

  public result: Observable<T> = this._resultSubject.asObservable()
  public process: Observable<any> = this._processSubject.asObservable();

}


@Injectable()
export class WampService {
  private _config: WebSocketSubjectConfig;
  private wsUrl: string = environment.wsUrl;
  public subject: WebSocketSubject<any>;

  private init() {
    this._config =  {
        url: `${this.wsUrl}/?token=${this.ar.currentUser.token}`,
    };
    this.subject = <WebSocketSubject<any>>WebSocketSubject.create(this._config);
    this.subject.subscribe((message) => {})
  }

  constructor(private ar: AuthResource) {
    if (!!this.ar.currentUser && !!this.ar.currentUser.token) {
      this.init();
    } else {
      this.ar.auth.subscribe(() => this.init());
    }
  }

  call<T>(endpoint: string, args?: any[], kwargs?: any): RpcCallObservable<T> {
    let message = {action: 'call', endpoint: endpoint, callee_uuid: uuid.v4(), args: args||[], kwargs: kwargs||{}};
    this.subject.next(JSON.stringify(message));
    return new RpcCallObservable<T>(
      this.subject,
      message.callee_uuid
    );
  }

  subscribe(endpoint, callback) {
    let message = {action: 'subscribe', endpoint: endpoint};
    this.subject.next(JSON.stringify(message));
    let subscription: Subscription = Observable.create((observer) => {
      this.subject.subscribe((message) => {
        observer.next(message)
      });
    }).filter(msg => msg.endpoint === endpoint)
      .subscribe(callback);
    return subscription
  }

  subscribeCallee(callee_uuid) {
    let message = {action: 'subscribe', endpoint: callee_uuid};
    this.subject.next(JSON.stringify(message));
    return new RpcCallObservable(
      this.subject,
      callee_uuid
    );
  }

  unsubscribe(endpoint) {
    let message = {action: 'unsubscribe', endpoint: endpoint};
    this.subject.next(JSON.stringify(message));
  }

}

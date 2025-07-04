﻿(function (v, w) {
  "object" === typeof exports && "undefined" !== typeof module
    ? (module.exports = w())
    : "function" === typeof define && define.amd
    ? define(w)
    : (v.ES6Promise = w());
})(this, function () {
  function v(a) {
    return "function" === typeof a;
  }
  function w() {
    return function () {
      return process.nextTick(n);
    };
  }
  function R() {
    return "undefined" !== typeof B
      ? function () {
          B(n);
        }
      : C();
  }
  function S() {
    var a = 0,
      b = new J(n),
      c = document.createTextNode("");
    b.observe(c, { characterData: !0 });
    return function () {
      c.data = a = ++a % 2;
    };
  }
  function T() {
    var a = new MessageChannel();
    a.port1.onmessage = n;
    return function () {
      return a.port2.postMessage(0);
    };
  }
  function C() {
    var a = setTimeout;
    return function () {
      return a(n, 1);
    };
  }
  function n() {
    for (var a = 0; a < k; a += 2)
      (0, q[a])(q[a + 1]), (q[a] = void 0), (q[a + 1] = void 0);
    k = 0;
  }
  function U() {
    try {
      var a = Function("return this")().require("vertx");
      B = a.runOnLoop || a.runOnContext;
      return R();
    } catch (b) {
      return C();
    }
  }
  function D(a, b) {
    var c = this,
      d = new this.constructor(r);
    void 0 === d[z] && K(d);
    var e = c._state;
    if (e) {
      var f = arguments[e - 1];
      l(function () {
        return L(e, d, f, c._result);
      });
    } else E(c, d, a, b);
    return d;
  }
  function F(a) {
    if (a && "object" === typeof a && a.constructor === this) return a;
    var b = new this(r);
    x(b, a);
    return b;
  }
  function r() {}
  function M(a) {
    try {
      return a.then;
    } catch (b) {
      return (p.error = b), p;
    }
  }
  function V(a, b, c, d) {
    try {
      a.call(b, c, d);
    } catch (e) {
      return e;
    }
  }
  function W(a, b, c) {
    l(function (a) {
      var e = !1,
        f = V(
          c,
          b,
          function (c) {
            e || ((e = !0), b !== c ? x(a, c) : m(a, c));
          },
          function (b) {
            e || ((e = !0), g(a, b));
          },
          "Settle: " + (a._label || " unknown promise")
        );
      !e && f && ((e = !0), g(a, f));
    }, a);
  }
  function X(a, b) {
    b._state === y
      ? m(a, b._result)
      : b._state === t
      ? g(a, b._result)
      : E(
          b,
          void 0,
          function (b) {
            return x(a, b);
          },
          function (b) {
            return g(a, b);
          }
        );
  }
  function N(a, b, c) {
    b.constructor === a.constructor && c === D && b.constructor.resolve === F
      ? X(a, b)
      : c === p
      ? (g(a, p.error), (p.error = null))
      : void 0 === c
      ? m(a, b)
      : v(c)
      ? W(a, b, c)
      : m(a, b);
  }
  function x(a, b) {
    if (a === b)
      g(a, new TypeError("You cannot resolve a promise with itself"));
    else {
      var c = typeof b;
      null === b || ("object" !== c && "function" !== c)
        ? m(a, b)
        : N(a, b, M(b));
    }
  }
  function Y(a) {
    a._onerror && a._onerror(a._result);
    G(a);
  }
  function m(a, b) {
    a._state === u &&
      ((a._result = b), (a._state = y), 0 !== a._subscribers.length && l(G, a));
  }
  function g(a, b) {
    a._state === u && ((a._state = t), (a._result = b), l(Y, a));
  }
  function E(a, b, c, d) {
    var e = a._subscribers,
      f = e.length;
    a._onerror = null;
    e[f] = b;
    e[f + y] = c;
    e[f + t] = d;
    0 === f && a._state && l(G, a);
  }
  function G(a) {
    var b = a._subscribers,
      c = a._state;
    if (0 !== b.length) {
      for (
        var d = void 0, e = void 0, f = a._result, g = 0;
        g < b.length;
        g += 3
      )
        (d = b[g]), (e = b[g + c]), d ? L(c, d, e, f) : e(f);
      a._subscribers.length = 0;
    }
  }
  function L(a, b, c, d) {
    var e = v(c),
      f = void 0,
      h = void 0,
      k = void 0,
      l = void 0;
    if (e) {
      try {
        f = c(d);
      } catch (n) {
        (p.error = n), (f = p);
      }
      f === p ? ((l = !0), (h = f.error), (f.error = null)) : (k = !0);
      if (b === f) {
        g(
          b,
          new TypeError("A promises callback cannot return that same promise.")
        );
        return;
      }
    } else (f = d), (k = !0);
    b._state === u &&
      (e && k ? x(b, f) : l ? g(b, h) : a === y ? m(b, f) : a === t && g(b, f));
  }
  function Z(a, b) {
    try {
      b(
        function (b) {
          x(a, b);
        },
        function (b) {
          g(a, b);
        }
      );
    } catch (c) {
      g(a, c);
    }
  }
  function K(a) {
    a[z] = O++;
    a._state = void 0;
    a._result = void 0;
    a._subscribers = [];
  }
  var H = void 0,
    P = (H = Array.isArray
      ? Array.isArray
      : function (a) {
          return "[object Array]" === Object.prototype.toString.call(a);
        }),
    k = 0,
    B = void 0,
    I = void 0,
    l = function (a, b) {
      q[k] = a;
      q[k + 1] = b;
      k += 2;
      2 === k && (I ? I(n) : Q());
    },
    A = (H = "undefined" !== typeof window ? window : void 0) || {},
    J = A.MutationObserver || A.WebKitMutationObserver,
    A =
      "undefined" === typeof self &&
      "undefined" !== typeof process &&
      "[object process]" === {}.toString.call(process),
    aa =
      "undefined" !== typeof Uint8ClampedArray &&
      "undefined" !== typeof importScripts &&
      "undefined" !== typeof MessageChannel,
    q = Array(1e3),
    Q = void 0,
    Q = A
      ? w()
      : J
      ? S()
      : aa
      ? T()
      : void 0 === H && "function" === typeof require
      ? U()
      : C(),
    z = Math.random().toString(36).substring(2),
    u = void 0,
    y = 1,
    t = 2,
    p = { error: null },
    O = 0,
    ba = (function () {
      function a(a, c) {
        this._instanceConstructor = a;
        this.promise = new a(r);
        this.promise[z] || K(this.promise);
        P(c)
          ? ((this._remaining = this.length = c.length),
            (this._result = Array(this.length)),
            0 === this.length
              ? m(this.promise, this._result)
              : ((this.length = this.length || 0),
                this._enumerate(c),
                0 === this._remaining && m(this.promise, this._result)))
          : g(this.promise, Error("Array Methods must be provided an Array"));
      }
      a.prototype._enumerate = function (a) {
        for (var c = 0; this._state === u && c < a.length; c++)
          this._eachEntry(a[c], c);
      };
      a.prototype._eachEntry = function (a, c) {
        var d = this._instanceConstructor,
          e = d.resolve;
        e === F
          ? ((e = M(a)),
            e === D && a._state !== u
              ? this._settledAt(a._state, c, a._result)
              : "function" !== typeof e
              ? (this._remaining--, (this._result[c] = a))
              : d === h
              ? ((d = new d(r)), N(d, a, e), this._willSettleAt(d, c))
              : this._willSettleAt(
                  new d(function (c) {
                    return c(a);
                  }),
                  c
                ))
          : this._willSettleAt(e(a), c);
      };
      a.prototype._settledAt = function (a, c, d) {
        var e = this.promise;
        e._state === u &&
          (this._remaining--, a === t ? g(e, d) : (this._result[c] = d));
        0 === this._remaining && m(e, this._result);
      };
      a.prototype._willSettleAt = function (a, c) {
        var d = this;
        E(
          a,
          void 0,
          function (a) {
            return d._settledAt(y, c, a);
          },
          function (a) {
            return d._settledAt(t, c, a);
          }
        );
      };
      return a;
    })(),
    h = (function () {
      function a(b) {
        this[z] = O++;
        this._result = this._state = void 0;
        this._subscribers = [];
        if (r !== b) {
          if ("function" !== typeof b)
            throw new TypeError(
              "You must pass a resolver function as the first argument to the promise constructor"
            );
          if (this instanceof a) Z(this, b);
          else
            throw new TypeError(
              "Failed to construct 'Promise': Please use the 'new' operator, this object constructor cannot be called as a function."
            );
        }
      }
      a.prototype["catch"] = function (a) {
        return this.then(null, a);
      };
      a.prototype["finally"] = function (a) {
        var c = this.constructor;
        return v(a)
          ? this.then(
              function (d) {
                return c.resolve(a()).then(function () {
                  return d;
                });
              },
              function (d) {
                return c.resolve(a()).then(function () {
                  throw d;
                });
              }
            )
          : this.then(a, a);
      };
      return a;
    })();
  h.prototype.then = D;
  h.all = function (a) {
    return new ba(this, a).promise;
  };
  h.race = function (a) {
    var b = this;
    return P(a)
      ? new b(function (c, d) {
          for (var e = a.length, f = 0; f < e; f++) b.resolve(a[f]).then(c, d);
        })
      : new b(function (a, b) {
          return b(new TypeError("You must pass an array to race."));
        });
  };
  h.resolve = F;
  h.reject = function (a) {
    var b = new this(r);
    g(b, a);
    return b;
  };
  h._setScheduler = function (a) {
    I = a;
  };
  h._setAsap = function (a) {
    l = a;
  };
  h._asap = l;
  h.polyfill = function () {
    var a = void 0;
    if ("undefined" !== typeof global) a = global;
    else if ("undefined" !== typeof self) a = self;
    else
      try {
        a = Function("return this")();
      } catch (b) {
        throw Error(
          "polyfill failed because global object is unavailable in this environment"
        );
      }
    var c = a.Promise;
    if (c) {
      var d = null;
      try {
        d = Object.prototype.toString.call(c.resolve());
      } catch (e) {}
      if ("[object Promise]" === d && !c.cast) return;
    }
    a.Promise = h;
  };
  return (h.Promise = h);
});

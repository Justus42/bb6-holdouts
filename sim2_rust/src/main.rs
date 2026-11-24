//! sim2: independent two-stack Turing machine simulator (bbchallenge text format).
//!
//! Usage: sim2 <machine> [step_limit]   (default step_limit = 100000000)

use std::process::exit;

#[derive(Clone, Copy, Debug)]
struct Trans {
    write: u8,
    right: bool,
    /// Some(i) = continue in state i; None = halt.
    next: Option<usize>,
}

fn fail(msg: &str) -> ! {
    eprintln!("error: {}", msg);
    exit(2);
}

/// Parse a machine in bbchallenge standard text format.
/// Returns (transition table indexed [state][symbol], number of symbols).
fn parse(machine: &str) -> Result<(Vec<Vec<Trans>>, usize), String> {
    if machine.is_empty() {
        return Err("empty machine string".into());
    }
    if !machine.is_ascii() {
        return Err("machine string must be ASCII".into());
    }
    let groups: Vec<&str> = machine.split('_').collect();
    let n_states = groups.len();
    if n_states > 26 {
        return Err(format!("too many states: {}", n_states));
    }
    let glen = groups[0].len();
    if glen == 0 || glen % 3 != 0 {
        return Err(format!("group 0 has invalid length {}", glen));
    }
    let n_symbols = glen / 3;
    if n_symbols < 2 || n_symbols > 10 {
        return Err(format!("unsupported number of symbols: {}", n_symbols));
    }
    let mut table = Vec::with_capacity(n_states);
    for (si, g) in groups.iter().enumerate() {
        if g.len() != glen {
            return Err(format!(
                "group {} has length {}, expected {}",
                si,
                g.len(),
                glen
            ));
        }
        let b = g.as_bytes();
        let mut row = Vec::with_capacity(n_symbols);
        for sym in 0..n_symbols {
            let t = &b[sym * 3..sym * 3 + 3];
            if t == b"---" {
                // Undefined transition: treated exactly like 1RZ.
                row.push(Trans { write: 1, right: true, next: None });
                continue;
            }
            let w = t[0];
            if !w.is_ascii_digit() || ((w - b'0') as usize) >= n_symbols {
                return Err(format!(
                    "state {} symbol {}: invalid write symbol '{}'",
                    si, sym, w as char
                ));
            }
            let right = match t[1] {
                b'R' => true,
                b'L' => false,
                c => {
                    return Err(format!(
                        "state {} symbol {}: invalid direction '{}'",
                        si, sym, c as char
                    ))
                }
            };
            let s = t[2];
            if !s.is_ascii_uppercase() {
                return Err(format!(
                    "state {} symbol {}: invalid next state '{}'",
                    si, sym, s as char
                ));
            }
            let idx = (s - b'A') as usize;
            let next = if idx < n_states { Some(idx) } else { None };
            row.push(Trans { write: w - b'0', right, next });
        }
        table.push(row);
    }
    Ok((table, n_symbols))
}

struct Tape {
    left: Vec<u8>,
    right: Vec<u8>,
    head: u8,
}

impl Tape {
    fn new() -> Self {
        Tape { left: Vec::new(), right: Vec::new(), head: 0 }
    }

    #[inline(always)]
    fn move_right(&mut self) {
        self.left.push(self.head);
        self.head = self.right.pop().unwrap_or(0);
    }

    #[inline(always)]
    fn move_left(&mut self) {
        self.right.push(self.head);
        self.head = self.left.pop().unwrap_or(0);
    }

    fn count_ones(&self) -> u64 {
        let c = |v: &Vec<u8>| v.iter().filter(|&&x| x == 1).count() as u64;
        c(&self.left) + c(&self.right) + if self.head == 1 { 1 } else { 0 }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 || args.len() > 3 {
        fail("usage: sim2 <machine> [step_limit]");
    }
    let machine = &args[1];
    let limit: u64 = if args.len() == 3 {
        match args[2].parse::<u64>() {
            Ok(v) => v,
            Err(_) => fail(&format!("invalid step_limit '{}'", args[2])),
        }
    } else {
        100_000_000
    };

    let (table, _n_symbols) = match parse(machine) {
        Ok(v) => v,
        Err(e) => fail(&format!("malformed machine '{}': {}", machine, e)),
    };

    let mut tape = Tape::new();
    let mut state: usize = 0;
    let mut steps: u64 = 0;
    let mut halted = false;

    while steps < limit {
        let t = table[state][tape.head as usize];
        tape.head = t.write;
        if t.right {
            tape.move_right();
        } else {
            tape.move_left();
        }
        steps += 1;
        match t.next {
            Some(s) => state = s,
            None => {
                halted = true;
                break;
            }
        }
    }

    println!(
        "{{\"machine\":\"{}\",\"halted\":{},\"steps\":{},\"ones\":{}}}",
        machine,
        halted,
        steps,
        tape.count_ones()
    );
}

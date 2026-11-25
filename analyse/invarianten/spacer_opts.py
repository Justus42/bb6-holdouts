import sys, time, z3
opts = {
 'standard': {},
 'ohne_slice_inline': {'fp.xform.slice': False, 'fp.xform.inline_linear': False, 'fp.xform.inline_eager': False},
 'global_gen': {'fp.spacer.global': True, 'fp.spacer.use_inductive_generalizer': True},
 'mbqi_arith': {'fp.spacer.arith.solver': 6},
}[sys.argv[1]]
z3.set_param('timeout', int(sys.argv[2])*1000)
s = z3.SolverFor('HORN')
for k, v in opts.items(): s.set(k.replace('fp.', 'fp.') if False else k, v) if False else z3.set_param(k, v)
s.from_file('rgr.smt2')
t = time.time(); r = s.check(); print(sys.argv[1], r, f'{time.time()-t:.1f}s')
if r == z3.sat: print(s.model())

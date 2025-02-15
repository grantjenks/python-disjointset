/*
 * disjointset.c
 *
 * This C extension implements a new abstract base type, DisjointSet,
 * which serves as a factory. When constructed with an integer n > 0,
 * it returns a StaticDisjointSet (using pre-allocated arrays). When constructed
 * with no argument or with n=None, it returns a DynamicDisjointSet (using dictionaries).
 *
 * Both StaticDisjointSet and DynamicDisjointSet inherit from DisjointSet.
 *
 * Version information is kept using the macro DISJOINTSET_VERSION.
 */

#include <Python.h>
#include <structmember.h>
#include <stdlib.h>

#ifndef DISJOINTSET_VERSION
#define DISJOINTSET_VERSION "1.0.0"
#endif

/******************************
 * Abstract Base: DisjointSet *
 ******************************/

typedef struct {
    PyObject_HEAD
    /* No instance-specific fields */
} DisjointSetObject;

/* Forward declaration of our concrete types */
PyTypeObject StaticDisjointSetType;
PyTypeObject DynamicDisjointSetType;

/*
 * Factory new method for DisjointSet.
 * If no argument is given or if the argument is None, a DynamicDisjointSet is returned.
 * If an integer > 0 is given, a StaticDisjointSet is returned.
 */

static PyObject *
DisjointSet_new(PyTypeObject *subtype, PyObject *args, PyObject *kwds)
{
    /* We expect at most one argument ("n") */
    Py_ssize_t nargs = PyTuple_Size(args);
    if (nargs == 0) {
        return PyObject_Call((PyObject *)&DynamicDisjointSetType, args, kwds);
    }
    else {
        PyObject *first;
        if (!PyArg_UnpackTuple(args, "DisjointSet", 0, 1, &first))
            return NULL;

        if (first == Py_None) {
            return PyObject_Call((PyObject *)&DynamicDisjointSetType, args, kwds);
        }

        if (PyLong_Check(first)) {
            Py_ssize_t n = PyLong_AsSsize_t(first);
            if (n <= 0) {
                PyErr_SetString(PyExc_ValueError, "n must be positive");
                return NULL;
            }
            return PyObject_Call((PyObject *)&StaticDisjointSetType, args, kwds);
        }
        else {
            PyErr_SetString(PyExc_TypeError, "n must be an integer or None");
            return NULL;
        }
    }
}

static PyTypeObject DisjointSetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "disjointset.DisjointSet",
    .tp_doc = "Abstract base class for disjoint sets.\n\n"
              "Call with an integer n to get a static disjoint set, or with None/nothing "
              "to get a dynamic disjoint set.",
    .tp_basicsize = sizeof(DisjointSetObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = DisjointSet_new,
};

/*******************************
 * StaticDisjointSet: Pre-allocated *
 *******************************/

typedef struct {
    DisjointSetObject base;  /* Inherit from DisjointSet */
    Py_ssize_t n;
    int *parent;  /* array of length n */
    int *rank;    /* array of length n */
} StaticDisjointSetObject;

/* Forward declaration of methods */
static int StaticDS_init(StaticDisjointSetObject *self, PyObject *args, PyObject *kwds);
static void StaticDS_dealloc(StaticDisjointSetObject *self);

/* Helper: iteratively find the representative for x with path splitting */
static int static_find(StaticDisjointSetObject *self, Py_ssize_t x) {
    while (self->parent[x] != x) {
        int temp = x;
        x = self->parent[x];
        self->parent[temp] = self->parent[x];
    }
    return x;
}

static PyObject *
StaticDS_find(StaticDisjointSetObject *self, PyObject *args)
{
    Py_ssize_t x;
    if (!PyArg_ParseTuple(args, "n", &x)) {
        return NULL;
    }
    if (x < 0 || x >= self->n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    int rep = static_find(self, x);
    return PyLong_FromLong(rep);
}

static PyObject *
StaticDS_union(StaticDisjointSetObject *self, PyObject *args)
{
    Py_ssize_t x, y;
    if (!PyArg_ParseTuple(args, "nn", &x, &y))
        return NULL;
    if (x < 0 || x >= self->n || y < 0 || y >= self->n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    int rootX = static_find(self, x);
    int rootY = static_find(self, y);
    if (rootX == rootY) {
        Py_RETURN_NONE;
    }
    if (self->rank[rootX] < self->rank[rootY]) {
        self->parent[rootX] = rootY;
    }
    else if (self->rank[rootX] > self->rank[rootY]) {
        self->parent[rootY] = rootX;
    }
    else {
        self->parent[rootY] = rootX;
        self->rank[rootX] += 1;
    }
    Py_RETURN_NONE;
}

static PyObject *
StaticDS_match(StaticDisjointSetObject *self, PyObject *args)
{
    Py_ssize_t x, y;
    if (!PyArg_ParseTuple(args, "nn", &x, &y))
        return NULL;
    if (x < 0 || x >= self->n || y < 0 || y >= self->n) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }
    int repX = static_find(self, x);
    int repY = static_find(self, y);
    if (repX == repY)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject *
StaticDS_sets(StaticDisjointSetObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *groups_dict = PyDict_New();
    if (!groups_dict)
        return NULL;
    for (Py_ssize_t i = 0; i < self->n; i++) {
        int rep = static_find(self, i);
        PyObject *rep_key = PyLong_FromLong(rep);
        if (!rep_key) {
            Py_DECREF(groups_dict);
            return NULL;
        }
        PyObject *group = PyDict_GetItem(groups_dict, rep_key);
        if (group == NULL) {
            group = PySet_New(NULL);
            if (!group) {
                Py_DECREF(rep_key);
                Py_DECREF(groups_dict);
                return NULL;
            }
            if (PyDict_SetItem(groups_dict, rep_key, group) < 0) {
                Py_DECREF(rep_key);
                Py_DECREF(group);
                Py_DECREF(groups_dict);
                return NULL;
            }
            Py_DECREF(group);
        }
        Py_DECREF(rep_key);

        PyObject *elem = PyLong_FromLong(i);
        if (!elem) {
            Py_DECREF(groups_dict);
            return NULL;
        }
        PyObject *rep_obj = PyLong_FromLong(static_find(self, i));
        if (!rep_obj) {
            Py_DECREF(elem);
            Py_DECREF(groups_dict);
            return NULL;
        }
        group = PyDict_GetItem(groups_dict, rep_obj);
        Py_DECREF(rep_obj);
        if (PySet_Add(group, elem) < 0) {
            Py_DECREF(elem);
            Py_DECREF(groups_dict);
            return NULL;
        }
        Py_DECREF(elem);
    }

    PyObject *outer_set = PySet_New(NULL);
    if (!outer_set) {
        Py_DECREF(groups_dict);
        return NULL;
    }
    PyObject *vals = PyDict_Values(groups_dict);
    if (!vals) {
        Py_DECREF(groups_dict);
        Py_DECREF(outer_set);
        return NULL;
    }
    Py_ssize_t len = PyList_Size(vals);
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *group = PyList_GetItem(vals, i);
        PyObject *froz = PyFrozenSet_New(group);
        if (!froz) {
            Py_DECREF(vals);
            Py_DECREF(groups_dict);
            Py_DECREF(outer_set);
            return NULL;
        }
        if (PySet_Add(outer_set, froz) < 0) {
            Py_DECREF(froz);
            Py_DECREF(vals);
            Py_DECREF(groups_dict);
            Py_DECREF(outer_set);
            return NULL;
        }
        Py_DECREF(froz);
    }
    Py_DECREF(vals);
    Py_DECREF(groups_dict);
    PyObject *result = PyFrozenSet_New(outer_set);
    Py_DECREF(outer_set);
    return result;
}

static PyMethodDef StaticDS_methods[] = {
    {"find", (PyCFunction)StaticDS_find, METH_VARARGS,
     "find(x): Return the representative of x."},
    {"union", (PyCFunction)StaticDS_union, METH_VARARGS,
     "union(x, y): Merge the sets containing x and y."},
    {"match", (PyCFunction)StaticDS_match, METH_VARARGS,
     "match(x, y): Return True if x and y are in the same set."},
    {"sets", (PyCFunction)StaticDS_sets, METH_NOARGS,
     "sets(): Return a frozenset of sets of connected nodes."},
    {NULL}
};

PyTypeObject StaticDisjointSetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "disjointset.StaticDisjointSet",
    .tp_doc = "Statically allocated disjoint set (n elements: 0 .. n-1)",
    .tp_basicsize = sizeof(StaticDisjointSetObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)StaticDS_init,
    .tp_dealloc = (destructor)StaticDS_dealloc,
    .tp_methods = StaticDS_methods,
};

static int
StaticDS_init(StaticDisjointSetObject *self, PyObject *args, PyObject *kwds)
{
    Py_ssize_t n;
    if (!PyArg_ParseTuple(args, "n", &n))
        return -1;
    if (n <= 0) {
        PyErr_SetString(PyExc_ValueError, "n must be positive");
        return -1;
    }
    self->n = n;
    self->parent = (int *)malloc(n * sizeof(int));
    self->rank = (int *)malloc(n * sizeof(int));
    if (self->parent == NULL || self->rank == NULL) {
        PyErr_SetString(PyExc_MemoryError, "unable to allocate memory");
        return -1;
    }
    for (Py_ssize_t i = 0; i < n; i++) {
        self->parent[i] = i;
        self->rank[i] = 0;
    }
    return 0;
}

static void
StaticDS_dealloc(StaticDisjointSetObject *self)
{
    if (self->parent)
        free(self->parent);
    if (self->rank)
        free(self->rank);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/********************************
 * DynamicDisjointSet: Dynamic *
 ********************************/

typedef struct {
    DisjointSetObject base;  /* Inherit from DisjointSet */
    PyObject *parent; /* dict: element -> representative */
    PyObject *rank;   /* dict: element -> rank (Python int) */
} DynamicDisjointSetObject;

static int DynamicDS_init(DynamicDisjointSetObject *self, PyObject *args, PyObject *kwds);
static void DynamicDS_dealloc(DynamicDisjointSetObject *self);

/* DynamicDS_find using path splitting */
static PyObject *
DynamicDS_find(DynamicDisjointSetObject *self, PyObject *args)
{
    PyObject *x;
    if (!PyArg_ParseTuple(args, "O", &x))
        return NULL;

    if (PyDict_Contains(self->parent, x) == 0) {
        if (PyDict_SetItem(self->parent, x, x) < 0)
            return NULL;
        PyObject *zero = PyLong_FromLong(0);
        if (!zero)
            return NULL;
        if (PyDict_SetItem(self->rank, x, zero) < 0) {
            Py_DECREF(zero);
            return NULL;
        }
        Py_DECREF(zero);
        Py_INCREF(x);
        return x;
    }

    /* Path splitting: update visited nodes along the find path */
    while (1) {
        PyObject *par = PyDict_GetItem(self->parent, x);  /* borrowed ref */
        int is_root = PyObject_RichCompareBool(par, x, Py_EQ);
        if (is_root < 0)
            return NULL;
        if (is_root == 1) {
            Py_INCREF(x);
            return x;
        }
        PyObject *grand = PyDict_GetItem(self->parent, par); /* borrowed ref */
        if (grand == NULL)
            return NULL;
        if (PyDict_SetItem(self->parent, x, grand) < 0)
            return NULL;
        x = par;
    }
    Py_RETURN_NONE;
}

static PyObject *
DynamicDS_union(DynamicDisjointSetObject *self, PyObject *args)
{
    PyObject *x, *y;
    if (!PyArg_ParseTuple(args, "OO", &x, &y))
        return NULL;
    PyObject *repX = PyObject_CallMethod((PyObject *)self, "find", "O", x);
    if (!repX)
        return NULL;
    PyObject *repY = PyObject_CallMethod((PyObject *)self, "find", "O", y);
    if (!repY) {
        Py_DECREF(repX);
        return NULL;
    }
    int equal = PyObject_RichCompareBool(repX, repY, Py_EQ);
    if (equal < 0) {
        Py_DECREF(repX);
        Py_DECREF(repY);
        return NULL;
    }
    if (equal == 1) {
        Py_DECREF(repX);
        Py_DECREF(repY);
        Py_RETURN_NONE;
    }
    PyObject *rankX = PyDict_GetItem(self->rank, repX);
    PyObject *rankY = PyDict_GetItem(self->rank, repY);
    if (!rankX || !rankY) {
        Py_DECREF(repX);
        Py_DECREF(repY);
        return NULL;
    }
    long rX = PyLong_AsLong(rankX);
    long rY = PyLong_AsLong(rankY);
    if (rX < 0 || rY < 0) {
        Py_DECREF(repX);
        Py_DECREF(repY);
        return NULL;
    }
    if (rX < rY) {
        if (PyDict_SetItem(self->parent, repX, repY) < 0) {
            Py_DECREF(repX);
            Py_DECREF(repY);
            return NULL;
        }
    }
    else if (rX > rY) {
        if (PyDict_SetItem(self->parent, repY, repX) < 0) {
            Py_DECREF(repX);
            Py_DECREF(repY);
            return NULL;
        }
    }
    else {
        if (PyDict_SetItem(self->parent, repY, repX) < 0) {
            Py_DECREF(repX);
            Py_DECREF(repY);
            return NULL;
        }
        PyObject *newRank = PyLong_FromLong(rX + 1);
        if (!newRank) {
            Py_DECREF(repX);
            Py_DECREF(repY);
            return NULL;
        }
        if (PyDict_SetItem(self->rank, repX, newRank) < 0) {
            Py_DECREF(newRank);
            Py_DECREF(repX);
            Py_DECREF(repY);
            return NULL;
        }
        Py_DECREF(newRank);
    }
    Py_DECREF(repX);
    Py_DECREF(repY);
    Py_RETURN_NONE;
}

static PyObject *
DynamicDS_match(DynamicDisjointSetObject *self, PyObject *args)
{
    PyObject *x, *y;
    if (!PyArg_ParseTuple(args, "OO", &x, &y))
        return NULL;
    PyObject *repX = PyObject_CallMethod((PyObject *)self, "find", "O", x);
    if (!repX)
        return NULL;
    PyObject *repY = PyObject_CallMethod((PyObject *)self, "find", "O", y);
    if (!repY) {
        Py_DECREF(repX);
        return NULL;
    }
    int same = PyObject_RichCompareBool(repX, repY, Py_EQ);
    Py_DECREF(repX);
    Py_DECREF(repY);
    if (same < 0)
        return NULL;
    if (same)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject *
DynamicDS_sets(DynamicDisjointSetObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *groups_dict = PyDict_New();
    if (!groups_dict)
        return NULL;
    PyObject *keys = PyDict_Keys(self->parent);
    if (!keys) {
        Py_DECREF(groups_dict);
        return NULL;
    }
    Py_ssize_t len = PyList_Size(keys);
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *elem = PyList_GetItem(keys, i);
        PyObject *rep = PyObject_CallMethod((PyObject *)self, "find", "O", elem);
        if (!rep) {
            Py_DECREF(keys);
            Py_DECREF(groups_dict);
            return NULL;
        }
        PyObject *group = PyDict_GetItem(groups_dict, rep);
        if (group == NULL) {
            group = PySet_New(NULL);
            if (!group) {
                Py_DECREF(rep);
                Py_DECREF(keys);
                Py_DECREF(groups_dict);
                return NULL;
            }
            if (PyDict_SetItem(groups_dict, rep, group) < 0) {
                Py_DECREF(rep);
                Py_DECREF(group);
                Py_DECREF(keys);
                Py_DECREF(groups_dict);
                return NULL;
            }
            Py_DECREF(group);
        }
        Py_DECREF(rep);

        PyObject *rep2 = PyObject_CallMethod((PyObject *)self, "find", "O", elem);
        if (!rep2) {
            Py_DECREF(keys);
            Py_DECREF(groups_dict);
            return NULL;
        }
        group = PyDict_GetItem(groups_dict, rep2);
        Py_DECREF(rep2);
        if (PySet_Add(group, elem) < 0) {
            Py_DECREF(keys);
            Py_DECREF(groups_dict);
            return NULL;
        }
    }
    Py_DECREF(keys);
    PyObject *outer_set = PySet_New(NULL);
    if (!outer_set) {
        Py_DECREF(groups_dict);
        return NULL;
    }
    PyObject *vals = PyDict_Values(groups_dict);
    if (!vals) {
        Py_DECREF(groups_dict);
        Py_DECREF(outer_set);
        return NULL;
    }
    len = PyList_Size(vals);
    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject *group = PyList_GetItem(vals, i);
        PyObject *froz = PyFrozenSet_New(group);
        if (!froz) {
            Py_DECREF(vals);
            Py_DECREF(groups_dict);
            Py_DECREF(outer_set);
            return NULL;
        }
        if (PySet_Add(outer_set, froz) < 0) {
            Py_DECREF(froz);
            Py_DECREF(vals);
            Py_DECREF(groups_dict);
            Py_DECREF(outer_set);
            return NULL;
        }
        Py_DECREF(froz);
    }
    Py_DECREF(vals);
    Py_DECREF(groups_dict);
    PyObject *result = PyFrozenSet_New(outer_set);
    Py_DECREF(outer_set);
    return result;
}

static PyMethodDef DynamicDS_methods[] = {
    {"find", (PyCFunction)DynamicDS_find, METH_VARARGS,
     "find(x): Return the representative of x."},
    {"union", (PyCFunction)DynamicDS_union, METH_VARARGS,
     "union(x, y): Merge the sets containing x and y."},
    {"match", (PyCFunction)DynamicDS_match, METH_VARARGS,
     "match(x, y): Return True if x and y are in the same set."},
    {"sets", (PyCFunction)DynamicDS_sets, METH_NOARGS,
     "sets(): Return a frozenset of sets of connected nodes."},
    {NULL}
};

PyTypeObject DynamicDisjointSetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "disjointset.DynamicDisjointSet",
    .tp_doc = "Dynamically allocated disjoint set (keys can be any hashable object)",
    .tp_basicsize = sizeof(DynamicDisjointSetObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)DynamicDS_init,
    .tp_dealloc = (destructor)DynamicDS_dealloc,
    .tp_methods = DynamicDS_methods,
};

static int
DynamicDS_init(DynamicDisjointSetObject *self, PyObject *args, PyObject *kwds)
{
    self->parent = PyDict_New();
    if (!self->parent)
        return -1;
    self->rank = PyDict_New();
    if (!self->rank) {
        Py_DECREF(self->parent);
        return -1;
    }
    return 0;
}

static void
DynamicDS_dealloc(DynamicDisjointSetObject *self)
{
    Py_XDECREF(self->parent);
    Py_XDECREF(self->rank);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/***************
 * Module Code *
 ***************/

static PyMethodDef module_methods[] = {
    {NULL}
};

static struct PyModuleDef disjointsetmodule = {
    PyModuleDef_HEAD_INIT,
    "disjointset",
    "Disjoint set data structures (abstract base DisjointSet with static and dynamic variants).",
    -1,
    module_methods,
};

PyMODINIT_FUNC
PyInit_disjointset(void)
{
    PyObject *m;
    if (PyType_Ready(&DisjointSetType) < 0)
        return NULL;

    /* Set up our concrete types to inherit from DisjointSet */
    StaticDisjointSetType.tp_base = &DisjointSetType;
    if (PyType_Ready(&StaticDisjointSetType) < 0)
        return NULL;

    DynamicDisjointSetType.tp_base = &DisjointSetType;
    if (PyType_Ready(&DynamicDisjointSetType) < 0)
        return NULL;

    m = PyModule_Create(&disjointsetmodule);
    if (m == NULL)
        return NULL;

    if (PyModule_AddObject(m, "DisjointSet", (PyObject *)&DisjointSetType) < 0) {
        Py_DECREF(&DisjointSetType);
        Py_DECREF(m);
        return NULL;
    }

    if (PyModule_AddObject(m, "StaticDisjointSet", (PyObject *)&StaticDisjointSetType) < 0) {
        Py_DECREF(&StaticDisjointSetType);
        Py_DECREF(m);
        return NULL;
    }

    if (PyModule_AddObject(m, "DynamicDisjointSet", (PyObject *)&DynamicDisjointSetType) < 0) {
        Py_DECREF(&DynamicDisjointSetType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}

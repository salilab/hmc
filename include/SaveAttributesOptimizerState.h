/**
 *  \file IMP/hmc/SaveAttributesOptimizerState.h
 *  \brief Store attributes of the model.
 *
 *  Copyright 2007-2019 IMP Inventors. All rights reserved.
 *
 */

#ifndef IMPHMC_SAVE_ATTRIBUTES_OPTIMIZER_STATE_H
#define IMPHMC_SAVE_ATTRIBUTES_OPTIMIZER_STATE_H

#include <IMP/hmc/hmc_config.h>
#include <IMP/hmc/ValueGradientInterface.h>
#include <IMP/OptimizerState.h>
#include <IMP/Model.h>
#include <IMP/Object.h>
#include <IMP/FloatIndex.h>
#include <IMP/Pointer.h>
#include <IMP/types.h>

IMPHMC_BEGIN_NAMESPACE

class IMPHMCEXPORT SaveAttributesOptimizerState : public OptimizerState {
  PointerMember<ValueGradientInterface> interface_;
  FloatsList vs_;

 public:
  SaveAttributesOptimizerState(ValueGradientInterface* interface);

  ValueGradientInterface* get_interface();

  FloatsList get_values() const;

 protected:
  virtual void do_update(unsigned int update_number) override;

  IMP_OBJECT_METHODS(SaveAttributesOptimizerState);
};

IMPHMC_END_NAMESPACE

#endif /* IMPHMC_SAVE_ATTRIBUTES_OPTIMIZER_STATE_H */

/*
 * Copyright (c) Contributors to the Open 3D Engine Project
 * 
 * SPDX-License-Identifier: Apache-2.0 OR MIT
 *
 */

#include <AzCore/Memory/SystemAllocator.h>
#include <AzCore/Module/Module.h>

namespace AtomTest
{
    class AtomTestModule
        : public AZ::Module
    {
    public:
        AZ_RTTI(AtomTestModule, "{250A1865-5494-4160-A6F3-0067F80CFDD2}", AZ::Module);
        AZ_CLASS_ALLOCATOR(AtomTestModule, AZ::SystemAllocator, 0);

        AtomTestModule()
            : AZ::Module()
        {
            // Push results of [MyComponent]::CreateDescriptor() into m_descriptors here.
            m_descriptors.insert(m_descriptors.end(), {
            });
        }

        /**
         * Add required SystemComponents to the SystemEntity.
         */
        AZ::ComponentTypeList GetRequiredSystemComponents() const override
        {
            return AZ::ComponentTypeList{
            };
        }
    };
}

// DO NOT MODIFY THIS LINE UNLESS YOU RENAME THE GEM
// The first parameter should be GemName_GemIdLower
// The second should be the fully qualified name of the class above
AZ_DECLARE_MODULE_CLASS(Gem_AtomTest, AtomTest::AtomTestModule)
